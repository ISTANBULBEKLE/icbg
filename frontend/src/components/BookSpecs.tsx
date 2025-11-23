"use client";

import React from 'react';
import styles from './BookSpecs.module.css';

interface BookSpecsProps {
    specs: {
        theme: string;
        humor: number;
        ageGroup: string;
    };
    onChange: (field: string, value: any) => void;
}

export default function BookSpecs({ specs, onChange }: BookSpecsProps) {
    return (
        <div className={styles.container}>
            <h3 className={styles.heading}>🎨 Book Specifications</h3>
            <p className={styles.description}>
                Customize the style and content of your children's book
            </p>
            <div className={styles.group}>
                <label className={styles.label}>Theme / Moral Lesson</label>
                <input
                    type="text"
                    className={styles.input}
                    placeholder="e.g., Honesty, Patience, Kindness"
                    value={specs.theme}
                    onChange={(e) => onChange('theme', e.target.value)}
                />
            </div>

            <div className={styles.group}>
                <label className={styles.label}>Humor Level (1-10): {specs.humor}</label>
                <input
                    type="range"
                    min="1"
                    max="10"
                    className={styles.range}
                    value={specs.humor}
                    onChange={(e) => onChange('humor', parseInt(e.target.value))}
                />
            </div>

            <div className={styles.group}>
                <label className={styles.label}>Target Age Group</label>
                <select
                    className={styles.input}
                    value={specs.ageGroup}
                    onChange={(e) => onChange('ageGroup', e.target.value)}
                >
                    <option value="3-5">3-5 years</option>
                    <option value="6-8">6-8 years</option>
                    <option value="9-12">9-12 years</option>
                </select>
            </div>
        </div>
    );
}
