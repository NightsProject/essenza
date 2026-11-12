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
    const mobileCompressionCards = document.getElementById('mobile-compression-cards');

    const compressionLevels = [10, 20, 30];
    const singleModelSelector = document.getElementById('single-model-selector');
    const singleModelSelect = document.getElementById('single-model-select');
    const generationModeRadios = document.querySelectorAll('input[name="generation_mode"]');
    let availableModels = [];

    // Mobile nav
    const navToggle = document.querySelector('.nav-toggle');
    const siteNav = document.getElementById('site-nav');

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
        generationModeRadios.forEach(radio => { radio.disabled = generating; });
        singleModelSelect.disabled = generating;
        progressSection.hidden = !generating;
        if (generating) {
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
    function updateProgress(percent, activeLabel = null) {
        progressBar.value = percent;
        progressValue.textContent = `${percent}%`;
        progressLabel.textContent = activeLabel
            ? `Generating ${activeLabel} summary…`
            : percent === 100 ? 'All model summaries complete' : 'Preparing next summary…';
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

    async function generateAllLevels(text, modelIds) {
        const sourceWordCount = countWords(text);
        const results = [];
        const totalWork = modelIds.length * compressionLevels.length;
        let completedWork = 0;

        for (const modelId of modelIds) {
            for (const level of compressionLevels) {
                const progress = Math.round((completedWork / totalWork) * 100);
                updateProgress(progress, `${getModelLabel(modelId)} · ${level}%`);
                try {
                    const result = await requestSummary(text, level, modelId);
                    results.push({ ...result, source_word_count: sourceWordCount, compression_level: level });
                } catch (error) {
                    results.push({
                        model_id: modelId,
                        model_label: getModelLabel(modelId),
                        source_word_count: sourceWordCount,
                        compression_level: level,
                        summary: '',
                        summary_word_count: 0,
                        actual_compression_percent: 0,
                        within_limit: false,
                        generation_time_ms: 0,
                        error: error.message || 'Generation failed',
                    });
                }
                completedWork += 1;
                updateProgress(Math.round((completedWork / totalWork) * 100), completedWork < totalWork ? 'Preparing next summary…' : null);
            }
        }

        renderAllLevelResults(results);
        resultsSection.hidden = false;
        updateProgress(100);
        scrollToResults();
    }

    function getModelLabel(modelId) {
        return availableModels.find(model => model.model_id === modelId)?.model_label || modelId;
    }

    function renderAllLevelResults(results) {
        resultsGrid.innerHTML = '';
        const groups = new Map();
        results.forEach(result => {
            if (!groups.has(result.model_id)) groups.set(result.model_id, []);
            groups.get(result.model_id).push(result);
        });

        groups.forEach((modelResults, modelId) => {
            const divider = document.createElement('h3');
            divider.className = 'model-results-divider';
            divider.textContent = getModelLabel(modelId);
            resultsGrid.appendChild(divider);
            modelResults.forEach(result => {
                const card = createResultCard({
                    modelLabel: `${result.compression_level}% maximum`,
                    summary: result.summary || '(summary unavailable)',
                    summaryWordCount: result.summary_word_count,
                    actualCompressionPercent: result.actual_compression_percent,
                    withinLimit: result.within_limit,
                    generationTimeMs: result.generation_time_ms,
                    error: result.error,
                    requestId: result.request_id,
                });
                resultsGrid.appendChild(card);
            });
        });

        renderCompressionSummaryTable(results);
        renderMobileCompressionCards(results);
        methodologyNote.hidden = false;
    }

    function renderCompressionSummaryTable(results) {
        const tableBody = document.getElementById('compression-summary-body');
        tableBody.replaceChildren();
        results.forEach(result => {
            const row = document.createElement('tr');
            const values = [
                result.model_label,
                String(result.source_word_count),
                `${result.compression_level}%`,
                String(Math.floor(result.source_word_count * result.compression_level / 100)),
                result.error ? '—' : String(result.summary_word_count),
                result.error ? '—' : formatRatio(result.actual_compression_percent),
                result.error ? 'Error' : result.within_limit ? 'Yes' : 'No',
                result.error ? '—' : `${result.generation_time_ms}ms`,
            ];
            values.forEach(value => {
                const cell = document.createElement('td');
                cell.textContent = value;
                row.appendChild(cell);
            });
            tableBody.appendChild(row);
        });
    }

    function renderMobileCompressionCards(results) {
        if (!mobileCompressionCards) return;
        mobileCompressionCards.innerHTML = '';
        results.forEach(result => {
            const card = document.createElement('article');
            card.className = `mobile-card ${result.within_limit ? 'within' : 'exceeds'}`;
            if (result.error) card.classList.add('error');
            
            const capBadgeClass = result.within_limit ? 'within' : 'exceeds';
            const capBadgeText = result.within_limit ? 'Within cap' : 'Exceeds cap';
            
            card.innerHTML = `
                <div class="mobile-header">
                    <span class="mobile-model">${escapeHtml(`${result.compression_level}% maximum`)}</span>
                    <span class="mobile-cap-badge ${capBadgeClass}">${escapeHtml(capBadgeText)}</span>
                </div>
                ${result.error ? `
                    <div class="mobile-error">Error: ${escapeHtml(result.error)}</div>
                ` : `
                    <div class="mobile-row"><span>Source words</span><strong>${result.source_word_count}</strong></div>
                    <div class="mobile-row"><span>Target words</span><strong>${Math.floor(result.source_word_count * result.compression_level / 100)}</strong></div>
                    <div class="mobile-row"><span>Summary words</span><strong>${result.summary_word_count}</strong></div>
                    <div class="mobile-row"><span>Actual compression</span><strong>${formatRatio(result.actual_compression_percent)}</strong></div>
                    <div class="mobile-row"><span>Generation time</span><strong>${result.generation_time_ms}ms</strong></div>
                `}
            `;
            mobileCompressionCards.appendChild(card);
        });
    }

    async function loadAvailableModels() {
        try {
            const response = await fetch(CONFIG.apiHealth);
            const data = await response.json();
            if (!response.ok) throw new Error(`Model list request failed: ${response.status}`);
            availableModels = data.models.filter(model => model.loaded);
            singleModelSelect.replaceChildren();
            availableModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                option.textContent = `${model.model_label} (${model.model_type})`;
                singleModelSelect.appendChild(option);
            });
            if (!availableModels.length) {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No loaded models available';
                option.disabled = true;
                option.selected = true;
                singleModelSelect.appendChild(option);
            } else {
                const preferred = availableModels.find(model => model.model_type === 'finetuned') || availableModels[0];
                singleModelSelect.value = preferred.model_id;
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            availableModels = [];
            singleModelSelect.replaceChildren();
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Failed to load models';
            option.disabled = true;
            option.selected = true;
            singleModelSelect.appendChild(option);
        }
        toggleModelSelector();
    }

    function toggleModelSelector() {
        const singleMode = document.querySelector('input[name="generation_mode"]:checked').value === 'single';
        singleModelSelector.hidden = !singleMode;
        btnText.textContent = singleMode ? 'Generate summaries for selected model' : 'Generate all summaries';
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
        const selectedMode = document.querySelector('input[name="generation_mode"]:checked').value;
        const modelIds = selectedMode === 'all'
            ? availableModels.map(model => model.model_id)
            : [singleModelSelect.value];
        if (!modelIds.length || modelIds.some(modelId => !modelId)) {
            showError('No loaded models are available. Check model status and try again.');
            return;
        }
        setGenerating(true);
        resultsSection.hidden = true;
        resultsGrid.innerHTML = '';
        currentRequestId = crypto.randomUUID().slice(0, 8);

        try {
            await generateAllLevels(text, modelIds);
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
    if (form) form.addEventListener('submit', handleSubmit);
    if (clearBtn) clearBtn.addEventListener('click', handleClear);
    if (sourceText) sourceText.addEventListener('input', updateWordCount);
    if (generationModeRadios.length) {
        generationModeRadios.forEach(radio => radio.addEventListener('change', toggleModelSelector));
    }

    // Mobile nav toggle
    if (navToggle && siteNav) {
        navToggle.addEventListener("click", () => {
            const isOpen = siteNav.classList.toggle("open");
            navToggle.setAttribute("aria-expanded", isOpen);
        });
        siteNav.querySelectorAll("a").forEach(link => {
            link.addEventListener("click", () => {
                siteNav.classList.remove("open");
                navToggle.setAttribute("aria-expanded", "false");
            });
        });
        document.addEventListener("keydown", (e) => {
            if (e.code === "Escape" && siteNav.classList.contains("open")) {
                siteNav.classList.remove("open");
                navToggle.setAttribute("aria-expanded", "false");
                navToggle.focus();
            }
        });
    }

    // Initialize
    if (sourceText) {
        updateWordCount();
        sourceText.focus();
    }
    loadAvailableModels();
    if (generationModeRadios.length) {
        toggleModelSelector();
    }

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