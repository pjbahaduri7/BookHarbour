import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus

def search_books_project_gutenberg(query):
    url = f"https://www.gutenberg.org/ebooks/search/?query={quote_plus(query)}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        soup = BeautifulSoup(response.text, "html.parser")

        book_info = []
        book_elements = soup.find_all("li", class_="booklink")
        for book_element in book_elements:
            title = book_element.find("span", class_="title").get_text()
            link = "https://www.gutenberg.org" + book_element.find("a")["href"]
            book_info.append((title, link))

        return book_info
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while searching Project Gutenberg: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while searching Project Gutenberg: {e}")
        return []

def search_books_openlibrary(query, search_by="title"):
    if search_by == "title":
        url = f"https://openlibrary.org/search?q={quote_plus(query)}"
    elif search_by == "genre":
        url = f"https://openlibrary.org/subjects/{quote_plus(query.replace(' ', '_'))}"
    elif search_by == "author":
        url = f"https://openlibrary.org/search?author={quote_plus(query)}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        soup = BeautifulSoup(response.text, "html.parser")

        book_info = []
        book_elements = soup.find_all(class_="booktitle")
        for book_element in book_elements:
            title = book_element.get_text()
            link = urljoin(url, book_element.find("a")["href"])
            book_info.append((title, link))

        return book_info
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while searching Open Library: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while searching Open Library: {e}")
        return []
