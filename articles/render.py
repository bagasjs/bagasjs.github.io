from typing import Dict, Tuple, Any
import os
from io import StringIO
from string import Template

html_template = Template(
"""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${title}</title>
        <link rel="stylesheet" href="/style.css">
    </head>
    <body>
        <div id="root">
            <header>
                <h1 id="logo">bagasjs</h1>
                <div class="menu">
                    <div class="menu-item"><a href="/">Home</a></div>
                    <div class="menu-item"><a href="/articles/articles.html">Articles</a></div>
                </div>
            </header>
            <section id="${section_name}">
                ${post}
            </section>
            <footer> 2026 BagasJS </footer>
        </div>
    </body>
</html>
""")

def translate_post_to_html(output: StringIO, source: str):
    lines = source.splitlines()
    in_ref_block = False
    prev_is_normal_text = False
    for line in lines:
        if line.startswith("#"):
            if prev_is_normal_text:
                output.write("</p>\n")
                prev_is_normal_text = False
            level = 0
            for ch in line:
                if ch != "#":
                    break
                level += 1
                if level >= 6:
                    break
            value = line[level:]
            output.write(f"<h{level} class=\"article-h{level}\">{value}</h{level}>\n")
        elif line.startswith("```"):
            if prev_is_normal_text:
                output.write("</p>\n")
                prev_is_normal_text = False
            in_ref_block = not in_ref_block 
            if in_ref_block:
                output.write("<div class=\"article-ref\">\n")
            else:
                output.write("</div>\n")
        elif line.startswith("=>"):
            if prev_is_normal_text:
                output.write("</p>\n")
                prev_is_normal_text = False
            line = line[2:].lstrip()
            url, value = line.split(None, maxsplit=1)
            output.write(f"<p><a href=\"{url}\">{value}</a></p>\n")
        elif len(line.lstrip()) == 0:
            if prev_is_normal_text:
                output.write("</p>\n")
                prev_is_normal_text = False
        else:
            if not prev_is_normal_text:
                output.write("<p class=\"article-p\">\n")
            output.write(f"{line}\n")
            prev_is_normal_text = True
            pass
    if prev_is_normal_text:
        output.write("</p>\n")
        prev_is_normal_text = False
    return source

def compile_post(filename: str, source: str) -> Tuple[Dict[str, Any], str]:
    # Peek if there's front-matter
    lines = source.splitlines()
    if lines[0].startswith("---"):
        pass
    i = 1
    metadata = {"__file__": filename }
    while i < len(lines):
        if lines[i].startswith("---"):
            i += 1
            break
        key, value = lines[i].split(":", maxsplit=1)
        metadata[key] = value
        i += 1
    body = "\n".join(lines[i:])
    output = StringIO()
    translate_post_to_html(output, body)
    return metadata, output.getvalue()

if __name__ == "__main__":
    posts = []
    for name in os.listdir(os.getcwd()):
        if not name.endswith(".gmi"):
            continue
        output_filename = f"{os.path.splitext(name)[0]}.html"
        with open(name, "r") as file:
            metadata, html = compile_post(name, file.read())
            html = html_template.substitute(title=metadata["title"], post=html, section_name="articles")
            with open(output_filename, "w") as outputf:
                outputf.write(html)
            posts.append(metadata)
    index_body =  '<h1 class="section-title"><a href="#articles">Articles</a></h1>\n'
    if len(posts) > 0:
        index_body += f'<ul style="list-style-position: inside;">\n'
        for post in posts:
            index_body += f'    <li><a href="/articles/2026-01-26.html">{post["title"]}</a>\n'
            index_body += f'        <p>{post["date"]}<p>\n'
            index_body += f'    </li>\n'
        index_body += f'</ul>\n'
    else:
        index_body += "<p>There's no article currently</p>"
    with open("articles.html", "w") as file:
        html = html_template.substitute(title="List of articles", post=index_body, section_name="posts")
        file.write(html)

