import os
import re
import textwrap
from datetime import datetime
from urllib.parse import urlparse, quote_plus, parse_qs

import mistune
from notion.client import NotionClient

import templates


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


def get_video_embed(source):
    url = urlparse(source)
    if url.netloc == "www.youtube.com":
        params = parse_qs(url.query)
        id_ = params["v"][0]
        return f'{{{{< youtube id="{id_}" autoplay="false" >}}}}'
    return ""


def blocks2md(blocks, indent=0):
    output_md = ""

    content = ""
    numbered_list_index = 0

    for i, block in enumerate(blocks):
        try:
            block_type = block.type
        except:
            continue

        try:
            block_title = block.title
        except:
            block_title = False

        if block_title:
            content = mistune.html(block_title) if block_title else ""
            content = content.strip()
            content = re.sub(r"^<p>", "", content)
            content = re.sub(r"</p>$", "", content)

        if block_type != "numbered_list":
            numbered_list_index = 0

        color = ""
        try:
            color = color if block.color is None else block.color
        except AttributeError:
            pass

        list_ = ""
        if block_type == "bulleted_list" or block_type == "numbered_list":
            list_ = " list"

        attrs = f' class="{color}{list_}"' if color or list_ else ""

        new_content = ""

        if block_type == "header":
            new_content = f"<h1{attrs}>{content}</h1>"
        elif block_type == "sub_header":
            new_content = f"<h2{attrs}>{content}</h2>"
        elif block_type == "sub_sub_header":
            new_content = f"<h3{attrs}>{content}</h3>"
        elif block_type == "text":
            new_content = f"<p{attrs}>{content}</p>"
        elif block_type == "bulleted_list" or block_type == "toggle":
            disc = '<div class="li_before"><div class="ul_disc">&bull;</div></div>'
            content = f"<p>{content}</p>"
            if block.children:
                content += "\n"
                content += blocks2md(block.children)
            content = f'<div class="li_content">{content}</div>'
            new_content = f"<div{attrs}>{disc}{content}</div>"
        elif block_type == "numbered_list":
            numbered_list_index += 1
            disc = f'<div class="li_before"><div class="ol_disc">{numbered_list_index}.</div></div>'
            content = f"<p>{content}</p>"
            if block.children:
                content += "\n"
                content += blocks2md(block.children)
            content = f'<div class="li_content">{content}</div>'
            new_content = f"<div{attrs}>{disc}{content}</div>"
        elif block_type == "to_do":
            if block.checked:
                checkbox = '<input type="checkbox" disabled checked>'
                new_content = f"<p>{checkbox}{content}</p>"
            else:
                checkbox = '<input type="checkbox" disabled>'
                new_content = f"<p>{checkbox}{content}</p>"
        elif block_type == "image":
            width = block.get()["format"]["block_width"]
            new_content = image("image", get_notion_img_link(block), width)
        elif block_type == "quote":
            content = ""
            for line in block_title.split("\n"):
                content += mistune.html(line)
            new_content = f"<blockquote{attrs}>" + content + "</blockquote>"
        elif block_type == "code":
            # You cannot color code blocks in notion
            new_content = "```" + block.language + "\n" + block.title + "\n```"
        elif block_type == "video":
            # or block_type == "file"
            # or block_type == "audio"
            # or block_type == "pdf"
            # or block_type == "gist"
            new_content = get_video_embed(block.source)
        elif block_type == "divider":
            new_content = f"<hr{attrs}>"
        # elif block_type == "bookmark":
        #     new_content = link(content, block.link)
        # elif block_type == "equation":
        #     new_content = "$$" + block.latex + "$$"
        # elif block_type == "column" or block_type == "column_list":
        #     continue
        # elif block_type == "page":
        #     try:
        #         if "https:" in block.icon:
        #             icon = "!" + link("", block.icon)
        #         else:
        #             icon = block.icon
        #         new_content = "# " + icon + content
        #     except:
        #         new_content = "# " + content
        else:
            print("Unkown type", block_type)

        output_md += new_content
        output_md += "\n\n"
        content = ""

    return output_md


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
    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
    client = NotionClient(token_v2=os.environ.get("NOTION_TOKEN", ""))

    articles = client.get_collection_view(
        "https://www.notion.so/danielfrg/1b48075329514ab785d68467ccbea7e9?v=3f8f32f695a549f085600d31f3680462"
    )
    articles = articles.collection.get_rows()

    this_dir = os.path.dirname(os.path.realpath(__file__))
    generated_dir = os.path.join(this_dir, "..", "content", "articles", "generated")

    i = None
    # i = len(articles) - 1

    subset = articles[i : i + 1] if i is not None else articles

    for row in subset:
        # for row in articles.collection.get_rows()[3:4]:
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
