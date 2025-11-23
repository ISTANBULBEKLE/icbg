import React from 'react';
import styles from '../app/page.module.css';

export interface Book {
    id: string;
    title: string;
    date: string;
    url: string;
}

interface BookHistoryDrawerProps {
    books: Book[];
    onDelete: (id: string) => void;
}

const BookHistoryDrawer: React.FC<BookHistoryDrawerProps> = ({ books, onDelete }) => {
    return (
        <div className={styles.drawer}>
            <h3 className={styles.drawerTitle}>Previous Books</h3>
            {books.length === 0 ? (
                <p className={styles.emptyState}>No books generated yet.</p>
            ) : (
                <ul className={styles.bookList}>
                    {books.map((book) => (
                        <li key={book.id} className={styles.bookItem}>
                            <div className={styles.bookInfo}>
                                <span className={styles.bookTitle}>{book.title}</span>
                                <span className={styles.bookDate}>{book.date}</span>
                            </div>
                            <div className={styles.bookActions}>
                                <a href={book.url} download="my_islamic_book.pdf" className={styles.downloadLink}>
                                    Download
                                </a>
                                <button
                                    className={styles.deleteButton}
                                    onClick={() => onDelete(book.id)}
                                    title="Delete book"
                                >
                                    Delete
                                </button>
                            </div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default BookHistoryDrawer;
