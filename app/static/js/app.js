// app/static/js/app.js — Essenza frontend interactions

(() => {
    'use strict';

    // ========================================================================
    // Configuration
    // ========================================================================
    const CONFIG = window.ESS_ENZA_CONFIG || {
        apiSummarize: '/api/summarize',
        apiCompare: '/api/compare',
    };

    // ========================================================================
    // State
    // ========================================================================
    let isGenerating = false;
    let currentRequestId = null;

    // ========================================================================
    // DOM Elements
    // ========================================================================
    const form = document.getElementById('summarize-form');
    const sourceText = document.getElementById('source-text');
    const sourceWordCount = document.getElementById('source-word-count');
    const clearBtn = document.getElementById('clear-btn');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const btnLoading = generateBtn.querySelector('.btn-loading');
    const resultsSection = document.getElementById('results');
    const resultsGrid = document.getElementById('results-grid');
    const methodologyNote = document.getElementById('methodology-note');

    // Radio groups
    const thresholdRadios = document.querySelectorAll('input[name="max_compression_percent"]');
    const modelModeRadios = document.querySelectorAll('input[name="model_mode"]');

    // ========================================================================
    // Utilities
    // ========================================================================
    function countWords(text) {
        if (!text || !text.trim()) return 0;
        return text.trim().split(/\s+/).filter(w => w.length > 0).length;
    }

    function formatRatio(ratio) {
        return ratio.toFixed(1) + '%';
    }

    function showError(message, target = sourceText) {
        target.setAttribute('aria-invalid', 'true');
        const hint = document.getElementById('source-hint');
        hint.textContent = message;
        hint.classList.remove('form-hidden');
        target.focus();
    }

    function clearError(target = sourceText) {
        target.removeAttribute('aria-invalid');
        const hint = document.getElementById('source-hint');
        hint.textContent = '';
        hint.classList.add('form-hidden');
    }

    function setGenerating(generating) {
        isGenerating = generating;
        generateBtn.disabled = generating;
        sourceText.disabled = generating;
        thresholdRadios.forEach(r => r.disabled = generating);
        modelModeRadios.forEach(r => r.disabled = generating);
        clearBtn.disabled = generating;

        if (generating) {
            btnText.hidden = true;
            btnLoading.hidden = false;
        } else {
            btnText.hidden = false;
            btnLoading.hidden = true;
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML; // Safe: textContent escapes HTML entities
    }

    // ========================================================================
    // Word Count
    // ========================================================================
    function updateWordCount() {
        const count = countWords(sourceText.value);
        sourceWordCount.textContent = `Source words: ${count}`;

        // Warn on very short text
        const hint = document.getElementById('source-hint');
        if (count > 0 && count < 50) {
            hint.textContent = 'Note: Very short text may produce unreliable compression ratios.';
            hint.classList.remove('form-hidden');
        } else if (!hint.textContent.includes('Note:')) {
            clearError();
        }
    }

    // ========================================================================
    // Form Actions
    // ========================================================================
    async function handleSubmit(event) {
        event.preventDefault();

        if (isGenerating) return;

        const text = sourceText.value.trim();
        if (!text) {
            showError('Please enter some text to summarize.');
            return;
        }

        const threshold = parseInt(document.querySelector('input[name="max_compression_percent"]:checked').value, 10);
        const modelMode = document.querySelector('input[name="model_mode"]:checked').value;

        clearError();
        setGenerating(true);
        resultsSection.hidden = true;
        resultsGrid.innerHTML = '';

        currentRequestId = crypto.randomUUID().slice(0, 8);

        try {
            if (modelMode === 'finetuned') {
                await callSummarize(text, threshold);
            } else {
                await callCompare(text, threshold);
            }
        } catch (error) {
            console.error('Generation error:', error);
            showError(error.message || 'An unexpected error occurred. Please try again.');
        } finally {
            setGenerating(false);
        }
    }

    async function callSummarize(text, threshold) {
        const response = await fetch(CONFIG.apiSummarize, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_text: text,
                max_compression_percent: threshold,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error?.message || `Request failed: ${response.status}`);
        }

        renderResult(data);
        resultsSection.hidden = false;
        scrollToResults();
    }

    async function callCompare(text, threshold) {
        const response = await fetch(CONFIG.apiCompare, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_text: text,
                max_compression_percent: threshold,
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error?.message || `Request failed: ${response.status}`);
        }

        renderComparison(data);
        resultsSection.hidden = false;
        scrollToResults();
    }

    // ========================================================================
    // Rendering
    // ========================================================================
    function renderResult(data) {
        const card = createResultCard({
            modelLabel: data.model_label,
            summary: data.summary,
            summaryWordCount: data.summary_word_count,
            actualCompressionPercent: data.actual_compression_percent,
            withinLimit: data.within_limit,
            generationTimeMs: data.generation_time_ms,
            requestId: data.request_id,
        });
        resultsGrid.innerHTML = '';
        resultsGrid.appendChild(card);
        methodologyNote.hidden = false;
    }

    function renderComparison(data) {
        resultsGrid.innerHTML = '';

        data.results.forEach(result => {
            const card = createResultCard({
                modelLabel: result.model_label,
                summary: result.summary || '(failed)',
                summaryWordCount: result.summary_word_count,
                actualCompressionPercent: result.actual_compression_percent,
                withinLimit: result.within_limit,
                generationTimeMs: result.generation_time_ms,
                error: result.error,
                requestId: data.request_id,
            });
            resultsGrid.appendChild(card);
        });

        methodologyNote.hidden = false;
    }

    function createResultCard({ modelLabel, summary, summaryWordCount, actualCompressionPercent, withinLimit, generationTimeMs, error, requestId }) {
        const card = document.createElement('article');
        card.className = `result-card ${withinLimit ? 'within' : 'exceeds'}`;
        if (error) card.classList.add('error');

        const capStatusClass = withinLimit ? 'within' : 'exceeds';
        const capStatusText = withinLimit ? 'Within cap' : 'Exceeds cap';

        card.innerHTML = `
            <div class="result-header">
                <span class="result-model">${escapeHtml(modelLabel)}</span>
                <span class="result-cap-status ${capStatusClass}">${escapeHtml(capStatusText)}</span>
            </div>
            <div class="result-summary" aria-label="Generated summary">${escapeHtml(summary)}</div>
            <div class="result-metrics">
                <span><strong>${summaryWordCount}</strong> words</span>
                <span>${formatRatio(actualCompressionPercent)} compression</span>
                <span>${generationTimeMs}ms</span>
            </div>
            <div class="result-actions">
                ${!error ? `
                    <button class="btn-copy" data-summary="${escapeHtml(summary).replace(/"/g, '"')}" aria-label="Copy summary to clipboard">
                        Copy summary
                    </button>
                ` : ''}
                ${error ? `<span class="error-message" style="color: var(--color-error); font-size: var(--text-sm);">Error: ${escapeHtml(error)}</span>` : ''}
            </div>
        `;

        // Copy button handler
        const copyBtn = card.querySelector('.btn-copy');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => copyToClipboard(copyBtn));
        }

        return card;
    }

    async function copyToClipboard(button) {
        const summary = button.dataset.summary;
        try {
            await navigator.clipboard.writeText(summary);
            button.textContent = 'Copied!';
            button.classList.add('copied');
            setTimeout(() => {
                button.textContent = 'Copy summary';
                button.classList.remove('copied');
            }, 2000);
        } catch (e) {
            console.error('Copy failed:', e);
            button.textContent = 'Failed';
            setTimeout(() => { button.textContent = 'Copy summary'; }, 2000);
        }
    }

    function scrollToResults() {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function handleClear() {
        sourceText.value = '';
        updateWordCount();
        clearError();
        resultsSection.hidden = true;
        resultsGrid.innerHTML = '';
        methodologyNote.hidden = true;
        sourceText.focus();
    }

    // ========================================================================
    // Event Listeners
    // ========================================================================
    form.addEventListener('submit', handleSubmit);
    clearBtn.addEventListener('click', handleClear);
    sourceText.addEventListener('input', updateWordCount);

    // Initialize
    updateWordCount();
    sourceText.focus();

    // Announce generation status for screen readers
    function announceStatus(message) {
        const announcer = document.createElement('div');
        announcer.setAttribute('role', 'status');
        announcer.setAttribute('aria-live', 'polite');
        announcer.className = 'sr-only';
        announcer.textContent = message;
        document.body.appendChild(announcer);
        setTimeout(() => announcer.remove(), 1000);
    }

    // Override setGenerating to announce
    const originalSetGenerating = setGenerating;
    setGenerating = function(generating) {
        originalSetGenerating(generating);
        if (generating) {
            announceStatus('Generating summary, please wait');
        } else {
            announceStatus('Summary generation complete');
        }
    };

})();