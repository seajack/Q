// 页面头部组件
class PageHeader {
    constructor(options = {}) {
        this.options = {
            title: '页面标题',
            subtitle: '页面描述信息',
            showBreadcrumb: false,
            breadcrumb: [],
            actions: [],
            notifications: 0,
            showSearch: true,
            ...options
        };
    }
    
    render() {
        return `
            <header class="page-header">
                <div class="header-content">
                    <div class="header-left">
                        ${this.renderBreadcrumb()}
                        ${this.renderTitle()}
                    </div>
                    <div class="header-right">
                        ${this.renderActions()}
                    </div>
                </div>
            </header>
        `;
    }
    
    renderBreadcrumb() {
        if (!this.options.showBreadcrumb || !this.options.breadcrumb.length) {
            return '';
        }
        
        const breadcrumbItems = this.options.breadcrumb.map((item, index) => {
            const isLast = index === this.options.breadcrumb.length - 1;
            return `
                <span class="breadcrumb-item ${isLast ? 'active' : ''}">
                    ${item.link && !isLast ? `<a href="${item.link}">${item.label}</a>` : item.label}
                </span>
                ${!isLast ? '<i class="fas fa-chevron-right breadcrumb-separator"></i>' : ''}
            `;
        }).join('');
        
        return `
            <nav class="breadcrumb">
                ${breadcrumbItems}
            </nav>
        `;
    }
    
    renderTitle() {
        return `
            <div class="title-section">
                <h1 class="page-title">${this.options.title}</h1>
                ${this.options.subtitle ? `<p class="page-subtitle">${this.options.subtitle}</p>` : ''}
            </div>
        `;
    }
    
    renderActions() {
        const searchButton = this.options.showSearch ? `
            <button class="header-action-btn" data-action="search">
                <i class="fas fa-search"></i>
            </button>
        ` : '';
        
        const notificationButton = `
            <button class="header-action-btn notification-btn" data-action="notifications">
                <i class="fas fa-bell"></i>
                ${this.options.notifications > 0 ? `<span class="notification-badge">${this.options.notifications}</span>` : ''}
            </button>
        `;
        
        const actionButtons = this.options.actions.map(action => `
            <button class="btn ${action.type || 'btn-primary'}" data-action="${action.id}">
                ${action.icon ? `<i class="${action.icon}"></i>` : ''}
                <span>${action.label}</span>
            </button>
        `).join('');
        
        return `
            <div class="header-actions">
                ${searchButton}
                ${notificationButton}
                ${actionButtons}
            </div>
        `;
    }
    
    mount(container) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        container.innerHTML = this.render();
        this.bindEvents(container);
        return this;
    }
    
    bindEvents(container) {
        const actionButtons = container.querySelectorAll('[data-action]');
        
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const action = button.dataset.action;
                this.handleAction(action, button);
            });
        });
    }
    
    handleAction(action, button) {
        switch (action) {
            case 'search':
                this.showSearchModal();
                break;
            case 'notifications':
                this.showNotifications();
                break;
            default:
                // 触发自定义事件
                const event = new CustomEvent('headerAction', {
                    detail: { action, button }
                });
                document.dispatchEvent(event);
        }
    }
    
    showSearchModal() {
        // 显示搜索模态框
        console.log('显示搜索');
    }
    
    showNotifications() {
        // 显示通知列表
        console.log('显示通知');
    }
    
    updateNotifications(count) {
        this.options.notifications = count;
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }
    
    updateTitle(title, subtitle = null) {
        this.options.title = title;
        if (subtitle !== null) {
            this.options.subtitle = subtitle;
        }
        
        const titleElement = document.querySelector('.page-title');
        const subtitleElement = document.querySelector('.page-subtitle');
        
        if (titleElement) {
            titleElement.textContent = title;
        }
        
        if (subtitleElement && subtitle !== null) {
            subtitleElement.textContent = subtitle;
        }
    }
}

// 页面头部样式
const headerStyles = `
<style>
.page-header {
    background: white;
    border-bottom: 1px solid var(--gray-200);
    padding: 1.5rem;
}

.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 100%;
}

.header-left {
    flex: 1;
}

.breadcrumb {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.breadcrumb-item {
    color: var(--gray-600);
}

.breadcrumb-item.active {
    color: var(--gray-900);
    font-weight: 500;
}

.breadcrumb-item a {
    color: var(--primary);
    text-decoration: none;
}

.breadcrumb-item a:hover {
    text-decoration: underline;
}

.breadcrumb-separator {
    margin: 0 0.5rem;
    color: var(--gray-400);
    font-size: 0.75rem;
}

.title-section {
    margin: 0;
}

.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--gray-900);
    margin: 0;
}

.page-subtitle {
    font-size: 1rem;
    color: var(--gray-600);
    margin: 0.25rem 0 0 0;
}

.header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.header-action-btn {
    width: 2.5rem;
    height: 2.5rem;
    border: none;
    background: transparent;
    border-radius: var(--radius);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gray-500);
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
}

.header-action-btn:hover {
    background-color: var(--gray-100);
    color: var(--gray-700);
}

.notification-btn {
    position: relative;
}

.notification-badge {
    position: absolute;
    top: -0.25rem;
    right: -0.25rem;
    width: 1rem;
    height: 1rem;
    background-color: var(--error);
    color: white;
    border-radius: 50%;
    font-size: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
}

@media (max-width: 768px) {
    .page-header {
        padding: 1rem;
    }
    
    .header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .header-right {
        width: 100%;
        justify-content: flex-end;
    }
    
    .page-title {
        font-size: 1.25rem;
    }
    
    .page-subtitle {
        font-size: 0.875rem;
    }
}
</style>
`;

// 导出组件
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PageHeader, headerStyles };
} else if (typeof window !== 'undefined') {
    window.PageHeader = PageHeader;
    window.headerStyles = headerStyles;
}
