import os
import re
from datetime import datetime
from urllib.parse import urlparse, quote_plus, parse_qs

import mistune
from slugify import slugify
from notion.client import NotionClient

import templates


def blocks2html(blocks):
    output = ""

    numbered_list_index = 0

    for i, block in enumerate(blocks):
        try:
            block_type = block.type
        except:
            continue

        if block_type != "numbered_list":
            numbered_list_index = 0

        classes = []
        if block_type == "bulleted_list" or block_type == "numbered_list":
            classes.append("notion-list")

        new_content = ""

        if block_type == "header":
            new_content = header(block, 1)
        elif block_type == "sub_header":
            new_content = header(block, 2)
        elif block_type == "sub_sub_header":
            new_content = header(block, 3)
        elif block_type == "text":
            new_content = p(block)
        elif block_type == "quote":
            new_content = blockquote(block)
        elif block_type == "code":
            # You cannot do color code blocks in notion
            new_content = code(block)
        elif block_type == "divider":
            new_content = divider(block)
        elif block_type == "bulleted_list":
            new_content = bulleted_list(block)
        elif block_type == "numbered_list":
            numbered_list_index += 1
            new_content = numbered_list(block, numbered_list_index)
        elif block_type == "to_do":
            new_content = todo(block)
        elif block_type == "image":
            new_content = img(block)
        elif block_type == "video":
            new_content = video(block)
        elif block_type == "column_list":
            new_content = column_list(block)
        # elif block_type == "file":
        # elif block_type == "audio":
        # elif block_type == "pdf":
        # elif block_type == "gist":
        # elif block_type == "toogle":
        # elif block_type == "bookmark":
        #     new_content = bookmark(content, block.link)
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

        output += new_content
        output += "\n\n"
        content = ""

    return output


def clean_content(block):
    try:
        content = mistune.html(block.title)
        content = content.strip()
        # Clean tags
        content = re.sub(r"^<p>", "", content)
        content = re.sub(r"</p>$", "", content)
        return content
    except:
        return ""


def make_attrs(block, width=None, extra_classes=None):
    attrs = ""
    classes = []
    # default to empty list
    extra_classes = extra_classes or []

    # Get color class
    color_cls = get_color_cls(block)
    if color_cls:
        classes.append(color_cls)

    # Add
    classes = extra_classes + classes

    # Make attrs
    if len(classes) > 0:
        cls = " ".join(classes)
        attrs += f' class="{cls}"'

    if width is not None:
        attrs += f' style="width: {width}px"' if width else ""

    return attrs


def get_color_cls(block):
    color = ""
    try:
        color = color if block.color is None else block.color
        return color
    except AttributeError:
        return None


def header(block, level):
    attrs = make_attrs(block)
    content = clean_content(block)
    return f"<h{level}{attrs}>{content}</h{level}>"


def p(block):
    attrs = make_attrs(block)
    content = clean_content(block)
    return f"<p{attrs}>{content}</p>"


def blockquote(block):
    attrs = make_attrs(block)
    content = clean_content(block)
    return f"<blockquote{attrs}>{content}</blockquote>"


def code(block):
    # Code blocks cannot have color
    language = block.language
    content = block.title
    return f"```{language}\n{content}\n```"


def divider(block):
    attrs = make_attrs(block)
    return f"<hr{attrs}>"


def bulleted_list(block):
    attrs = make_attrs(block, extra_classes=["notion-list"])
    content = clean_content(block)
    content = f"<p>{content}</p>\n"
    disc = '<div class="li_before"><div class="ul_disc">&bull;</div></div>'

    if block.children:
        content += blocks2html(block.children) + "\n"
    content = f'<div class="li_content">\n{content}\n</div>\n'
    return f"<div{attrs}>\n{disc}\n{content}</div>"


def numbered_list(block, index=1):
    attrs = make_attrs(block, extra_classes=["notion-list"])
    content = clean_content(block)
    content = f"<p>{content}</p>\n"
    disc = f'<div class="li_before"><div class="ol_disc">{index}.</div></div>'

    if block.children:
        content += blocks2html(block.children) + "\n"
    content = f'<div class="li_content">\n{content}\n</div>\n'
    return f"<div{attrs}>\n{disc}\n{content}</div>"


def todo(block):
    attrs = make_attrs(block)
    content = clean_content(block)

    if block.checked:
        checkbox = '<input type="checkbox" disabled checked>'
        return f"<p{attrs}>{checkbox}{content}</p>\n"
    else:
        checkbox = '<input type="checkbox" disabled>'
        return f"<p{attrs}>{checkbox}{content}</p>\n"


def img(block):
    name = ""
    url = get_img_link(block)
    width = block.get()["format"]["block_width"]
    attrs = make_attrs(block, width=width)
    return f'<img alt="{name}" src="{url}" {attrs} />'


def get_img_link(block):
    image_block = block.get()
    block_id = image_block["id"]
    url_quote = quote_plus(image_block["format"]["display_source"])

    notion_img_template = (
        "https://www.notion.so/image/{url}?table=block&id={id}&userId=&cache=v2"
    )
    return notion_img_template.format(url=url_quote, id=block_id)


def video(block):
    source = block.source
    url = urlparse(source)
    if url.netloc == "www.youtube.com":
        params = parse_qs(url.query)
        id_ = params["v"][0]
        iframe = f'<iframe src="https://www.youtube.com/embed/{id_}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:0;" allowfullscreen="" title="YouTube Video"></iframe>'
        return f'<div class="notion-video" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">{iframe}</div>'
    return ""


def column_list(block):
    output = '<div class="notion-column-list d-flex flex-row">'
    for column in block.children:
        ratio = column.column_ratio
        col_content = f'<div class="notion-column" style="flex: {ratio} {ratio} 0;" >'
        col_content += blocks2html(column.children)
        col_content += f"</div>"
        output += col_content
    output += "</div>"
    return output


################################################################################


def featured_image(blocks):
    for block in blocks:
        try:
            block_type = block.type
        except:
            continue

        if block_type == "image":
            return get_img_link(block)
    return ""


def get_md(page):
    title = page.name
    slug = slugify(title)
    date = page.publish_date.start if page.publish_date else datetime(2100, 1, 1)
    date_str = date.strftime("%Y-%m-%d")

    page_url = page.get_browseable_url()
    page = client.get_block(page_url)
    body = blocks2html(page.children)
    # body = f'<div class="notion-page">\n{body}\n</div>'

    feature_image = featured_image(page.children)
    summary = page.summary
    tags = page.tags
    published = page.published
    draft = not published
    print(draft)

    return templates.article.format(
        title=title,
        slug=slug,
        date=date_str,
        feature_image=feature_image,
        summary=summary,
        tags=tags,
        draft=draft,
        body=body,
    ).strip()


if __name__ == "__main__":
    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
    token = os.environ.get("NOTION_TOKEN", "")
    table_url = os.environ.get("NOTION_TABLE_URL", "")

    assert token is not None
    assert token != ""
    assert table_url is not None
    assert table_url != ""

    client = NotionClient(token_v2=token)

    articles = client.get_collection_view(table_url)
    articles = articles.collection.get_rows()

    this_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(this_dir, "..", "content", "articles", "generated-notion")

    i = None

    # i = 0
    # i = len(articles) - 1

    subset = articles[i : i + 1] if i is not None else articles

    for row in subset:
        title = row.name
        print("Generating:", title)
        date_dir = str(row.publish_date.start.year) if row.publish_date else "drafts"

        output_dir_ = os.path.join(output_dir, date_dir)
        os.makedirs(output_dir_, exist_ok=True)
        print(output_dir)
        fname = slugify(title) + ".md"
        output_file = os.path.join(output_dir_, fname)
        md_content = get_md(row)

        with open(output_file, "w") as f:
            f.write(md_content)
