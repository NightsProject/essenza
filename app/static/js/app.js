// app/static/js/app.js — Essenza frontend interactions

(() => {
    'use strict';

    // ========================================================================
    // Configuration
    // ========================================================================
    const CONFIG = window.ESS_ENZA_CONFIG || {
        apiSummarize: '/api/summarize',
        apiCompare: '/api/compare',
        apiHealth: '/health',
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
    const progressSection = document.getElementById('generation-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressLabel = document.getElementById('progress-label');
    const progressValue = document.getElementById('progress-value');
    const generationError = document.getElementById('generation-error');

    const singleModelSelector = document.getElementById('single-model-selector');
    const singleModelSelect = document.getElementById('single-model-select');
    const modelModeRadios = document.querySelectorAll('input[name="model_mode"]');
    const compressionLevels = [10, 20, 30];
    const totalSteps = compressionLevels.length;

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
        clearBtn.disabled = generating;
        modelModeRadios.forEach(radio => { radio.disabled = generating; });
        singleModelSelect.disabled = generating;
        progressSection.hidden = !generating;
        if (!generating) {
            progressBar.value = 100;
            progressValue.textContent = '100%';
            progressLabel.textContent = 'All compression levels complete';
        } else {
            updateProgress(0);
        }

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
    // Progress
    // ========================================================================
    function updateProgress(completedSteps, activeLevel = null) {
        const percent = Math.round((completedSteps / totalSteps) * 100);
        progressBar.value = percent;
        progressValue.textContent = `${percent}%`;
        progressLabel.textContent = activeLevel === null
            ? 'Preparing summaries…'
            : `Generating ${activeLevel}% compression summary…`;
    }

    async function requestSummary(text, threshold, modelId) {
        const response = await fetch(CONFIG.apiSummarize, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_text: text,
                max_compression_percent: threshold,
                model_id: modelId,
            }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error?.message || data.detail?.error?.message || `Request failed: ${response.status}`);
        }
        return data;
    }

    async function generateAllLevels(text, modelId) {
        const results = [];
        for (let index = 0; index < compressionLevels.length; index += 1) {
            const level = compressionLevels[index];
            updateProgress(index, level);
            const result = await requestSummary(text, level, modelId);
            results.push({ ...result, compression_level: level });
            updateProgress(index + 1, index + 1 < totalSteps ? compressionLevels[index + 1] : null);
        }
        renderAllLevelResults(results);
        resultsSection.hidden = false;
        scrollToResults();
    }

    function renderAllLevelResults(results) {
        resultsGrid.innerHTML = '';
        results.forEach(result => {
            const card = createResultCard({
                modelLabel: `${result.model_label} — ${result.compression_level}% maximum`,
                summary: result.summary,
                summaryWordCount: result.summary_word_count,
                actualCompressionPercent: result.actual_compression_percent,
                withinLimit: result.within_limit,
                generationTimeMs: result.generation_time_ms,
                requestId: result.request_id,
            });
            resultsGrid.appendChild(card);
        });
        methodologyNote.hidden = false;
    }

    async function loadAvailableModels() {
        try {
            const response = await fetch(CONFIG.apiHealth);
            const data = await response.json();
            const models = data.models.filter(model => model.loaded);
            singleModelSelect.replaceChildren();
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                option.textContent = `${model.model_label} (${model.model_type})`;
                singleModelSelect.appendChild(option);
            });
            const preferred = models.find(model => model.model_type === 'finetuned') || models[0];
            if (preferred) singleModelSelect.value = preferred.model_id;
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    }

    function toggleModelSelector() {
        singleModelSelector.hidden = document.querySelector('input[name="model_mode"]:checked').value !== 'single';
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

        clearError();
        generationError.hidden = true;
        setGenerating(true);
        resultsSection.hidden = true;
        resultsGrid.innerHTML = '';
        currentRequestId = crypto.randomUUID().slice(0, 8);

        try {
            const selectedMode = document.querySelector('input[name="model_mode"]:checked').value;
            const selectedModelId = selectedMode === 'compare' ? 'baseline' : singleModelSelect.value;
            await generateAllLevels(text, selectedModelId);
        } catch (error) {
            console.error('Generation error:', error);
            generationError.textContent = error.message || 'An unexpected error occurred. Please try again.';
            generationError.hidden = false;
            progressLabel.textContent = 'Generation stopped';
            showError(error.message || 'An unexpected error occurred. Please try again.');
        } finally {
            setGenerating(false);
        }
    }

    // ========================================================================
    // Rendering
    // ========================================================================

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
    modelModeRadios.forEach(radio => radio.addEventListener('change', toggleModelSelector));

    // Initialize
    updateWordCount();
    loadAvailableModels();
    toggleModelSelector();
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