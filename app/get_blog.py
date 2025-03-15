import argparse
import re
import requests
import ollama

from bs4 import BeautifulSoup
import sqlite3

from .database import *

# from .database import init_db, get_cached_url, cache_url


def ask_model(prompt):
    response = ollama.chat(
        model="llama3.2",
        # model="deepseek-coder-v2:latest",
        options={"num_ctx": 32768},
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()


def fetch_html(url):
    """Fetch HTML content from a given URL."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


# def find_blog_post_tag(html):
def find_blog_post_tag(html):
    """Use LLM to determine the HTML tag that contains the blog post."""
    prompt = (
        "You are an AI that analyzes HTML structure. "
        "Identify the main HTML tag that contains a blog post."
        'Respond with the tag type (such as "h1" or "div" and attributes in JSON format: {"tag": "<tag>", "attributes": {<attr>: <value>}}.\n\n'
        f"HTML Content:\n{html[:5000]}"
        "The response MUST be in proper JSON format, written so that the html tag can be searched for using other tools."
    )
    response = ask_model(prompt)

    return response


def extract_blog_content(html, tag_info):
    tag_info = eval(find_blog_post_tag(html))  # Ensure correct JSON parsing
    soup = BeautifulSoup(html, "html.parser")
    blog_post = soup.find(tag_info["tag"], tag_info.get("attributes", {}))

    if blog_post:
        title = blog_post.find("h1") or blog_post.find("h2")
        title_text = title.get_text(strip=True) if title else "Untitled"
        content_text = blog_post.get_text(strip=True)
        return {"title": title_text, "content": content_text}
    return None


# write actual checks here
def check_for_success(data):
    if data:
        return True
    return False


def main(args):

    if not args.url:
        url = (
            "https://www.kmx.io/blog/why-stopped-everything-and-started-writing-C-again"
        )
    else:
        url = args.url

    try:
        html = fetch_html(url)
        blog_tag = find_blog_post_tag(html)
        blog_data = extract_blog_content(html, blog_tag)
        success = check_for_success(blog_data)

        if blog_data:
            save_to_db(url, blog_data["title"], html, blog_data["content"], success)
            print("Blog post saved successfully!")
        else:
            print("No blog post found.")

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script with a test flag.")
    parser.add_argument("-t", "--test", action="store_true", help="Enable test mode")
    parser.add_argument("-u", "--url", type=str, help="URL of blog")
    args = parser.parse_args()

    main(args)
