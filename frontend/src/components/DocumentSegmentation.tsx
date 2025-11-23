"use client";

import React from 'react';
import styles from './DocumentSegmentation.module.css';

interface DocumentSegmentationProps {
    segmentation: {
        sectionDescription: string;
        additionalContext: string;
        pageStart: number | null;
        pageEnd: number | null;
    };
    onChange: (field: string, value: any) => void;
}

export default function DocumentSegmentation({ segmentation, onChange }: DocumentSegmentationProps) {
    return (
        <div className={styles.container}>
            <h3 className={styles.heading}>📖 Specify Document Section</h3>
            <p className={styles.description}>
                Tell us which part of the document to use for the children's book
            </p>

            <div className={styles.group}>
                <label className={styles.label}>
                    Section Description
                    <span className={styles.required}>*</span>
                </label>
                <input
                    type="text"
                    className={styles.input}
                    placeholder="e.g., Surah Maryam, Chapter 3: The Battle of Badr, Story of Prophet Yusuf"
                    value={segmentation.sectionDescription}
                    onChange={(e) => onChange('sectionDescription', e.target.value)}
                />
                <p className={styles.hint}>
                    Describe the section you want to focus on. Our AI will find the relevant content.
                </p>
            </div>

            <div className={styles.group}>
                <label className={styles.label}>
                    Additional Context
                    <span className={styles.optional}>(optional)</span>
                </label>
                <textarea
                    className={styles.textarea}
                    placeholder="e.g., Focus on the verses about Prophet Isa's birth, Include the story of the palm tree"
                    value={segmentation.additionalContext}
                    onChange={(e) => onChange('additionalContext', e.target.value)}
                    rows={3}
                />
                <p className={styles.hint}>
                    Add any extra details to help us identify the exact content you want.
                </p>
            </div>

            <div className={styles.divider}>
                <span className={styles.dividerText}>OR specify page range</span>
            </div>

            <div className={styles.pageRange}>
                <div className={styles.pageGroup}>
                    <label className={styles.label}>Start Page</label>
                    <input
                        type="number"
                        className={styles.pageInput}
                        placeholder="1"
                        min="1"
                        value={segmentation.pageStart || ''}
                        onChange={(e) => onChange('pageStart', e.target.value ? parseInt(e.target.value) : null)}
                    />
                </div>
                <span className={styles.pageSeparator}>to</span>
                <div className={styles.pageGroup}>
                    <label className={styles.label}>End Page</label>
                    <input
                        type="number"
                        className={styles.pageInput}
                        placeholder="10"
                        min="1"
                        value={segmentation.pageEnd || ''}
                        onChange={(e) => onChange('pageEnd', e.target.value ? parseInt(e.target.value) : null)}
                    />
                </div>
            </div>
            <p className={styles.hint}>
                If you know the exact page numbers, you can specify them here.
            </p>
        </div>
    );
}
