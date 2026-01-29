document.addEventListener('DOMContentLoaded', function () {
    // Styling for the suggestion box
    const style = document.createElement('style');
    style.textContent = `
        .search-suggestions-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            z-index: 1000;
            background: white;
            border: 1px solid #ddd;
            border-radius: 0 0 4px 4px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-height: 300px;
            overflow-y: auto;
            display: none;
            text-align: left;
        }
        .suggestion-item {
            padding: 8px 12px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
        }
        .suggestion-item:last-child {
            border-bottom: none;
        }
        .suggestion-item:hover {
            background-color: #f8f9fa;
        }
        .suggestion-category {
            font-size: 0.75rem;
            color: #6c757d;
            text-transform: uppercase;
            margin-bottom: 2px;
        }
        .suggestion-value {
            font-weight: 500;
            color: #212529;
        }
    `;
    document.head.appendChild(style);

    const searchInputs = document.querySelectorAll('input[type="search"][data-suggestion-url], input[name="q"][data-suggestion-url]');

    searchInputs.forEach(input => {
        // Ensure parent is relative for positioning
        const parent = input.parentElement;
        const computedStyle = window.getComputedStyle(parent);
        if (computedStyle.position === 'static') {
            parent.style.position = 'relative';
        }

        const dropdown = document.createElement('div');
        dropdown.className = 'search-suggestions-dropdown';
        parent.appendChild(dropdown);

        let debounceTimer;

        input.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            const query = this.value.trim();
            const url = this.getAttribute('data-suggestion-url');

            if (query.length < 1) {
                dropdown.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`${url}?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        dropdown.innerHTML = '';
                        if (data.results && data.results.length > 0) {
                            data.results.forEach(result => {
                                const item = document.createElement('div');
                                item.className = 'suggestion-item';
                                item.innerHTML = `
                                    <div class="suggestion-category">${result.category}</div>
                                    <div class="suggestion-value">${result.label}</div>
                                `;
                                item.addEventListener('click', function () {
                                    input.value = result.value;
                                    dropdown.style.display = 'none';

                                    // If there's a specific URL in the result, go there (optional)
                                    // if (result.url) window.location.href = result.url;

                                    // Otherwise submit form
                                    if (input.form) {
                                        input.form.submit();
                                    }
                                });
                                dropdown.appendChild(item);
                            });
                            dropdown.style.display = 'block';
                        } else {
                            dropdown.style.display = 'none';
                        }
                    })
                    .catch(error => console.error('Error fetching suggestions:', error));
            }, 300);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            if (!parent.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    });
});
