import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import requests
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie

#set page configuration
st.set_page_config(
    page_title="📚Personal Library Managment System 📚",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

#custom css for styling
st.markdown("""
<style>
    .main-header{
        font-size: 3rem !important;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important;     
    }

    .sub_header {
        font-size: 1.8rem !important;
        color: #3882F6;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .success-message {
        padding: 1rem;
        background-color: #ECFDFS;
        border-left: 5px solid #108981;
        border-radius: 0.375rem;
    }

    .warning-message {
        padding: 1rem;
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        border-radius: 0.375rem;
    }

    .book-card {
        background-color: #3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3882F6;
        transition: transform 0.3s ease;
    } 

    .book-card-hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0,.1);
    }

    .read-badge {
        background-color: #108981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .unread-badge {
        background-color: #F87171;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .action-button {
        margin-right: 0.5rem;
    }

    .stButton>button {
        border-radius: 0.375rem;
    }

</style>
""", unsafe_allow_html=True)

def save_library():
    try:
        with open("library.json", "w") as file:  
            json.dump(st.session_state.library, file, indent=4)  
    except Exception as e:
        st.error(f"Error saving library: {e}")

# Load library function
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
        else:
            return False
    except Exception as e:
        st.error(f"Error Loading library: {e}")
        return False
    
if "library" not in st.session_state:
    st.session_state.library = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "book_added" not in st.session_state:
    st.session_state.book_added = False
if "book_removed" not in st.session_state:
    st.session_state.book_removed = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "Library"

# Add book function
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title' : title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)  # animation delay

# Remove book function
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True

# Search books function
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

# Calculate library state
def get_library_state():
    total_books = len(st.session_state.library)
   read_books = sum(1 for book in st.session_state.library if '📝read_status' in book and book['📝read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        # Count genres
        genres[book['genre']] = genres.get(book['genre'], 0) + 1

        # Count authors
        authors[book['author']] = authors.get(book['author'], 0) + 1

        # Count decades
        try:
            decade = (int(book['publication_year']) // 10) * 10
            decades[decade] = decades.get(decade, 0) + 1
        except ValueError:
            pass

    # Sorting by count
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'unread_books': total_books - read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Visualization creation
def create_visualization(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(
            data=[go.Pie(
                labels=['Read', 'Unread'],
                values=[stats['read_books'], stats['unread_books']],
                hole=0.4,
                marker_colors=['#108981', '#F87171']
            )]
        )
        fig_read_status.update_layout(
            title_text='Read vs Unread Books',
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)

    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genres': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df,
            x='Genres',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig_genres.update_layout(
            title_text='Books by Genre',
            xaxis_title='Genre',
            yaxis_title='Number of Books',
            height='400'
        )
        st.plotly_chart(fig_genres, use_container_width=True)

    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f'{decade}s' for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='spline'
        )
        fig_decades.update_layout(
            title_text='Books by Publication Decade',
            xaxis_title='Decade',
            yaxis_title='Number of Books',
            height=400
        )
        st.plotly_chart(fig_decades, use_container_width=True)

st.sidebar.markdown("<h1 style='text-align: center;'> Navigation</h1>", unsafe_allow_html=True)

# Lottie animation
def load_lottie_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

lottie_book = load_lottie_url("https://assets9.lottiefiles.com/temp/1f20_aKAFIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key='book_animation')

nav_option = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Book", "Library Statistics"]
)

if nav_option == "View Library":
    st.session_state.current_view = "Library"
elif nav_option == "Add Book":
    st.session_state.current_view = "Add"
elif nav_option == "Search Book":
    st.session_state.current_view = "Search"
elif nav_option == "Library Statistics":
    st.session_state.current_view = "Stats"

# Main header
st.markdown("<h1 class='main-header'> Personal Library Manager </h1>", unsafe_allow_html=True)

if st.session_state.current_view == "Add":
    st.markdown("<h2 class='sub_header'> Add a New Book</h2>", unsafe_allow_html=True)

    # Adding book input form
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2023)

        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "Romance", "History", "Thriller", "Psychology", "Philosophy", "Biographies"
            ])
            read_status = st.radio("Have you read this book?", ("Yes", "No"))

        submit_button = st.form_submit_button("Submit")
        if submit_button:
            add_book(title, author, publication_year, genre, read_status.lower() == "yes")
            st.success("Book added successfully!")

elif st.session_state.current_view == "Library":
    st.markdown("<h2 class='sub_header'> Your Library </h2>", unsafe_allow_html=True)
    for index, book in enumerate(st.session_state.library):
        book_card = f"""
        <div class="book-card">
            <h3>{book['title']}</h3>
            <p>by {book['author']}</p>
            <p>Published: {book['publication_year']}</p>
            <p>Genre: {book['genre']}</p>
            <p>Status: {'Read' if book['read_status'] else 'Unread'}</p>
            <p>
                <button class="action-button" onClick="remove_book({index})"> Remove </button>
            </p>
        </div>
        """
        st.markdown(book_card, unsafe_allow_html=True)

elif st.session_state.current_view == "Search":
    st.markdown("<h2 class='sub_header'> Search Books </h2>", unsafe_allow_html=True)

    search_term = st.text_input("Enter search term")
    search_by = st.radio("Search by", ["Title", "Author", "Genre"])

    search_button = st.button("Search")
    if search_button:
        search_books(search_term, search_by)
        if st.session_state.search_results:
            for book in st.session_state.search_results:
                st.write(f"{book['title']}** by {book['author']} ({book['publication_year']})")
        else:
            st.warning("No matching books found.")

elif st.session_state.current_view == "Stats":
    stats = get_library_state()
    st.markdown("<h2 class='sub_header'> Library Statistics </h2>", unsafe_allow_html=True)
    st.write(f"Total books: {stats['total_books']}")
    st.write(f"Books read: {stats['read_books']}")
    st.write(f"Books unread: {stats['unread_books']}")
    st.write(f"Percentage read: {stats['percent_read']:.2f}%")
    st.markdown("---")
st.markdown("Copyright @ 2025 Tayyaba Sheikh Personal Library Manager", unsafe_allow_html=True)
