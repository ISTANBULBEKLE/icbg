import React from 'react';
import styles from '../app/page.module.css';

export interface Book {
    id: string;
    title: string;
    date: string;
    url: string;
}

interface BookHistoryDrawerProps {
    sourceFiles: { name: string; date: string }[];
    generatedBooks: Book[];
    onDeleteBook: (id: string) => void;
    onDeleteSourceFile: (filename: string) => void;
}

const BookHistoryDrawer: React.FC<BookHistoryDrawerProps> = ({ sourceFiles, generatedBooks, onDeleteBook, onDeleteSourceFile }) => {
    return (
        <div className={styles.drawer}>
            {/* Source Files Section */}
            <div className={styles.drawerSection}>
                <h3 className={styles.drawerTitle}>Recent Source Files</h3>
                {sourceFiles.length === 0 ? (
                    <p className={styles.emptyState}>No files uploaded yet.</p>
                ) : (
                    <ul className={styles.bookList}>
                        {sourceFiles.map((file, index) => (
                            <li key={index} className={styles.bookItem}>
                                <div className={styles.bookInfo}>
                                    <span className={styles.bookTitle} style={{ fontSize: '0.85rem' }}>📄 {file.name}</span>
                                    <span className={styles.bookDate}>{file.date}</span>
                                </div>
                                <div className={styles.bookActions}>
                                    <a
                                        href={`http://localhost:8000/source_files/${file.name}`}
                                        download={file.name}
                                        className={styles.downloadLink}
                                        title="Download source file"
                                    >
                                        Download
                                    </a>
                                    <button
                                        className={styles.deleteButton}
                                        onClick={() => onDeleteSourceFile(file.name)}
                                        title="Delete source file"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* Generated Books Section */}
            <div className={styles.drawerSection} style={{ marginTop: '2rem' }}>
                <h3 className={styles.drawerTitle}>Previous Generated PDF Books</h3>
                {generatedBooks.length === 0 ? (
                    <p className={styles.emptyState}>No books generated yet.</p>
                ) : (
                    <ul className={styles.bookList}>
                        {generatedBooks.map((book) => (
                            <li key={book.id} className={styles.bookItem}>
                                <div className={styles.bookInfo}>
                                    <span className={styles.bookTitle}>📚 {book.title}</span>
                                    <span className={styles.bookDate}>{book.date}</span>
                                </div>
                                <div className={styles.bookActions}>
                                    <a
                                        href={book.url}
                                        download={`${book.title}.pdf`}
                                        className={styles.downloadLink}
                                    >
                                        Download
                                    </a>
                                    <button
                                        className={styles.deleteButton}
                                        onClick={() => onDeleteBook(book.id)}
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
        </div>
    );
};

export default BookHistoryDrawer;
