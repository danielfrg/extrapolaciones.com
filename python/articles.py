import os
import textwrap
from datetime import datetime
from urllib.parse import quote_plus

from notion.client import NotionClient

import templates


# Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
client = NotionClient(token_v2=os.environ.get("NOTION_TOKEN", ""))

articles = client.get_collection_view(
    "https://www.notion.so/danielfrg/1b48075329514ab785d68467ccbea7e9?v=3f8f32f695a549f085600d31f3680462"
)


def link(name, url):
    return "[" + name + "]" + "(" + url + ")"


def image(name, url, width=None):
    width = f'style="width: {width}px"' if width else ""
    return f'<img alt="{name}" src="{url}" {width} />'


def get_notion_img_link(block):
    image = block.get()
    block_id = image["id"]
    url_quote = quote_plus(image["format"]["display_source"])

    notion_img_template = (
        "https://www.notion.so/image/{url}?table=block&id={id}&userId=&cache=v2"
    )
    return notion_img_template.format(url=url_quote, id=block_id)


def blocks2md(blocks, indent=0):
    md = ""
    img_count = 0
    numbered_list_index = 0

    for block in blocks:
        try:
            btype = block.type
        except:
            continue

        if btype != "numbered_list":
            numbered_list_index = 0
        try:
            bt = block.title
        except:
            pass

        new_content = ""
        if btype == "header":
            new_content = "# " + bt
        elif btype == "sub_header":
            new_content = "## " + bt
        elif btype == "sub_sub_header":
            new_content = "### " + bt
        elif btype == "page":
            try:
                if "https:" in block.icon:
                    icon = "!" + link("", block.icon)
                else:
                    icon = block.icon
                new_content = "# " + icon + bt
            except:
                new_content = "# " + bt
        elif btype == "text":
            new_content = bt + "  "
        elif btype == "bookmark":
            new_content = link(bt, block.link)
        elif (
            btype == "video"
            or btype == "file"
            or btype == "audio"
            or btype == "pdf"
            or btype == "gist"
        ):
            new_content = link(block.source, block.source)
        elif btype == "bulleted_list" or btype == "toggle":
            new_content = "- " + bt
            if block.children:
                new_content += "\n"
                new_content += blocks2md(block.children, indent=indent + 2)
        elif btype == "numbered_list":
            numbered_list_index += 1
            new_content = str(numbered_list_index) + ". " + bt
            if block.children:
                new_content += "\n"
                new_content += blocks2md(block.children, indent=indent + 2)
        elif btype == "image":
            width = block.get()["format"]["block_width"]
            new_content = image("image", get_notion_img_link(block), width)
        elif btype == "code":
            new_content = "```" + block.language + "\n" + block.title + "\n```"
        elif btype == "equation":
            new_content = "$$" + block.latex + "$$"
        elif btype == "divider":
            new_content = "---"
        elif btype == "to_do":
            if block.checked:
                new_content = "- [x] " + bt
            else:
                new_content = "- [ ]" + bt
        elif btype == "quote":
            new_content = "> " + bt
        elif btype == "column" or btype == "column_list":
            continue
        else:
            print("Unkown type", btype)

        md += textwrap.indent(new_content, " " * indent)
        md += "\n\n"
    return md


def featured_image(blocks):
    for block in blocks:
        try:
            btype = block.type
        except:
            continue

        if btype == "image":
            return get_notion_img_link(block)
    return ""


def get_md(item):
    title = item.name

    page_url = item.get_browseable_url()
    page = client.get_block(page_url)
    body = blocks2md(page.children)

    feature_image = featured_image(page.children)
    tags = item.tags
    summary = item.summary
    published = row.published
    date = row.publish_date.start if row.publish_date else datetime(2100, 1, 1)
    date_str = date.strftime("%Y-%m-%d")
    draft = not published

    return templates.article.format(
        title=title,
        date=date_str,
        feature_image=feature_image,
        summary=summary,
        tags=tags,
        body=body,
        draft=draft,
    ).strip()


if __name__ == "__main__":
    this_dir = os.path.dirname(os.path.realpath(__file__))
    generated_dir = os.path.join(this_dir, "..", "content", "articles", "generated")

    for row in articles.collection.get_rows():
        title = row.name
        published = row.published
        date_dir = str(row.publish_date.start.year) if row.publish_date else "drafts"

        output_dir = os.path.join(generated_dir, date_dir)
        os.makedirs(output_dir, exist_ok=True)

        fname = title.lower().replace(" ", "-") + ".md"
        output_file = os.path.join(output_dir, fname)
        md_content = get_md(row)

        with open(output_file, "w") as f:
            f.write(md_content)
