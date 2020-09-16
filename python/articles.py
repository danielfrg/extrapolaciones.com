import os
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


def get_notion_img_link(block):
    notion_img_template = (
        "https://www.notion.so/image/{url}?table=block&id={id}&userId=&cache=v2"
    )
    image = block.get()
    url_quote = quote_plus(image["format"]["display_source"])
    block_id = image["id"]
    return notion_img_template.format(url=url_quote, id=block_id)


def block2md(blocks):
    md = ""
    img_count = 0
    numbered_list_index = 0
    # title = blocks[0].title
    # title = title.replace(" ", "")

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
        if btype == "header":
            md += "# " + bt
        elif btype == "sub_header":
            md += "## " + bt
        elif btype == "sub_sub_header":
            md += "### " + bt
        elif btype == "page":
            try:
                if "https:" in block.icon:
                    icon = "!" + link("", block.icon)
                else:
                    icon = block.icon
                md += "# " + icon + bt
            except:
                md += "# " + bt
        elif btype == "text":
            md += bt + "  "
        elif btype == "bookmark":
            md += link(bt, block.link)
        elif (
            btype == "video"
            or btype == "file"
            or btype == "audio"
            or btype == "pdf"
            or btype == "gist"
        ):
            md += link(block.source, block.source)
        elif btype == "bulleted_list" or btype == "toggle":
            md += "- " + bt
        elif btype == "numbered_list":
            numbered_list_index += 1
            md += str(numbered_list_index) + ". " + bt
        elif btype == "image":
            md += "!" + link("image", get_notion_img_link(block))
        elif btype == "code":
            md += "```" + block.language + "\n" + block.title + "\n```"
        elif btype == "equation":
            md += "$$" + block.latex + "$$"
        elif btype == "divider":
            md += "---"
        elif btype == "to_do":
            if block.checked:
                md += "- [x] " + bt
            else:
                md += "- [ ]" + bt
        elif btype == "quote":
            md += "> " + bt
        elif btype == "column" or btype == "column_list":
            continue
        else:
            pass
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
    date = item.publish_date.start
    date_str = date.strftime("%Y-%m-%d")
    page_url = item.get_browseable_url()
    page = client.get_block(page_url)
    body = block2md(page.children)

    feature_image = featured_image(page.children)
    tags = item.tags
    summary = item.summary

    return templates.article.format(
        title=title,
        date=date_str,
        feature_image=feature_image,
        summary=summary,
        tags=tags,
        body=body,
    ).strip()


if __name__ == "__main__":
    this_dir = os.path.dirname(os.path.realpath(__file__))
    generated_dir = os.path.join(this_dir, "..", "content", "articles", "generated")

    for row in articles.collection.get_rows():
        date = row.publish_date.start

        output_dir = os.path.join(generated_dir, str(date.year))
        os.makedirs(output_dir, exist_ok=True)

        fname = row.name.lower().replace(" ", "-") + ".md"
        output_file = os.path.join(output_dir, fname)
        md_content = get_md(row)

        with open(output_file, "w") as f:
            f.write(md_content)
