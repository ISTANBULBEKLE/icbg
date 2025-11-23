"use client";

import React, { useCallback } from 'react';
import styles from './UploadZone.module.css';

interface UploadZoneProps {
    onFileSelect: (file: File) => void;
}

export default function UploadZone({ onFileSelect }: UploadZoneProps) {
    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onFileSelect(e.dataTransfer.files[0]);
        }
    }, [onFileSelect]);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            onFileSelect(e.target.files[0]);
        }
    }, [onFileSelect]);

    return (
        <div
            className={styles.container}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => document.getElementById('fileInput')?.click()}
        >
            <input
                type="file"
                id="fileInput"
                style={{ display: 'none' }}
                onChange={handleChange}
                accept=".pdf,.epub"
            />
            <div className={styles.icon}>📚</div>
            <div className={styles.text}>Upload Islamic Literature (PDF/EPUB)</div>
            <div className={styles.subtext}>Drag & drop or click to browse</div>
        </div>
    );
}
