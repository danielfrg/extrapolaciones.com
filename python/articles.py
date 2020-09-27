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
    numbered_list_index = 0

    for block in blocks:
        try:
            block_type = block.type
        except:
            print(0)
            continue

        try:
            block_title = block.title
        except:
            pass

        if block_type != "numbered_list":
            numbered_list_index = 0

        color = ""
        try:
            color = color if block.color is None else block.color
        except AttributeError:
            pass

        print(block)

        attrs = f'class="{color}"' if color else ""
        new_content = ""
        if block_type == "header":
            new_content = f"<h1{attrs}>{block_title}</h1>"
        elif block_type == "sub_header":
            new_content = f"<h2{attrs}>{block_title}</h2>"
        elif block_type == "sub_sub_header":
            new_content = f"<h3{attrs}>{block_title}</h3>"
        elif block_type == "text":
            new_content = f"<p{attrs}>{block_title}</p>"
        elif block_type == "bulleted_list" or block_type == "toggle":
            new_content = "- " + block_title
            if block.children:
                new_content += "\n"
                new_content += blocks2md(block.children, indent=indent + 2)
        elif block_type == "numbered_list":
            numbered_list_index += 1
            new_content = str(numbered_list_index) + ". " + block_title
            if block.children:
                new_content += "\n"
                new_content += blocks2md(block.children, indent=indent + 2)
        elif block_type == "image":
            width = block.get()["format"]["block_width"]
            new_content = image("image", get_notion_img_link(block), width)
        elif block_type == "quote":
            new_content = "> " + block_title
        elif block_type == "code":
            new_content = "```" + block.language + "\n" + block.title + "\n```"
        elif block_type == "bookmark":
            new_content = link(block_title, block.link)
        elif (
            block_type == "video"
            or block_type == "file"
            or block_type == "audio"
            or block_type == "pdf"
            or block_type == "gist"
        ):
            new_content = link(block.source, block.source)
        elif block_type == "equation":
            new_content = "$$" + block.latex + "$$"
        elif block_type == "divider":
            new_content = "---"
        elif block_type == "to_do":
            if block.checked:
                new_content = "- [x] " + block_title
            else:
                new_content = "- [ ]" + block_title
        elif block_type == "column" or block_type == "column_list":
            continue
        elif block_type == "page":
            try:
                if "https:" in block.icon:
                    icon = "!" + link("", block.icon)
                else:
                    icon = block.icon
                new_content = "# " + icon + block_title
            except:
                new_content = "# " + block_title
        else:
            print("Unkown type", block_type)

        md += textwrap.indent(new_content, " " * indent)
        md += "\n\n"
    return md


def featured_image(blocks):
    for block in blocks:
        try:
            block_type = block.type
        except:
            continue

        if block_type == "image":
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

    # for row in articles.collection.get_rows()[:]:
    for row in articles.collection.get_rows()[3:4]:
        title = row.name
        print(title)
        published = row.published
        date_dir = str(row.publish_date.start.year) if row.publish_date else "drafts"

        output_dir = os.path.join(generated_dir, date_dir)
        os.makedirs(output_dir, exist_ok=True)

        fname = title.lower().replace(" ", "-") + ".md"
        output_file = os.path.join(output_dir, fname)
        md_content = get_md(row)

        with open(output_file, "w") as f:
            f.write(md_content)
