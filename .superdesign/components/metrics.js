// 指标卡片组件
class MetricCard {
    constructor(options = {}) {
        this.options = {
            title: '指标标题',
            value: '0',
            subtitle: '指标描述',
            icon: 'fas fa-chart-line',
            iconColor: 'primary',
            trend: null, // { value: '+12%', direction: 'up', label: '较上月' }
            progress: null, // { value: 75, label: '完成率' }
            emoji: null,
            onClick: null,
            ...options
        };
    }
    
    render() {
        return `
            <div class="metric-card ${this.options.onClick ? 'clickable' : ''}" ${this.options.onClick ? 'data-clickable="true"' : ''}>
                <div class="metric-header">
                    <div class="metric-icon ${this.options.iconColor}">
                        <i class="${this.options.icon}"></i>
                    </div>
                    ${this.options.emoji ? `<span class="metric-emoji">${this.options.emoji}</span>` : ''}
                </div>
                <div class="metric-content">
                    <h3 class="metric-value">${this.options.value}</h3>
                    <p class="metric-title">${this.options.title}</p>
                    ${this.options.subtitle ? `<p class="metric-subtitle">${this.options.subtitle}</p>` : ''}
                </div>
                ${this.renderFooter()}
            </div>
        `;
    }
    
    renderFooter() {
        if (this.options.trend) {
            return `
                <div class="metric-footer">
                    <div class="metric-trend ${this.options.trend.direction}">
                        <i class="fas fa-arrow-${this.options.trend.direction}"></i>
                        <span>${this.options.trend.value} ${this.options.trend.label || ''}</span>
                    </div>
                </div>
            `;
        }
        
        if (this.options.progress) {
            return `
                <div class="metric-footer">
                    <div class="metric-progress">
                        <div class="progress">
                            <div class="progress-bar" style="width: ${this.options.progress.value}%"></div>
                        </div>
                        <span class="progress-label">${this.options.progress.value}% ${this.options.progress.label || ''}</span>
                    </div>
                </div>
            `;
        }
        
        return '';
    }
    
    mount(container) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        const cardElement = document.createElement('div');
        cardElement.innerHTML = this.render();
        const card = cardElement.firstElementChild;
        
        if (this.options.onClick) {
            card.addEventListener('click', this.options.onClick);
        }
        
        container.appendChild(card);
        return card;
    }
    
    update(newOptions) {
        this.options = { ...this.options, ...newOptions };
        // 重新渲染逻辑
    }
}

// 指标网格组件
class MetricsGrid {
    constructor(options = {}) {
        this.options = {
            columns: 4,
            gap: '1.5rem',
            metrics: [],
            ...options
        };
        this.cards = [];
    }
    
    render() {
        return `
            <div class="metrics-grid" style="grid-template-columns: repeat(${this.options.columns}, 1fr); gap: ${this.options.gap};">
                ${this.options.metrics.map(metric => new MetricCard(metric).render()).join('')}
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
        const clickableCards = container.querySelectorAll('.metric-card[data-clickable="true"]');
        
        clickableCards.forEach((card, index) => {
            const metric = this.options.metrics[index];
            if (metric.onClick) {
                card.addEventListener('click', metric.onClick);
            }
        });
    }
    
    addMetric(metric) {
        this.options.metrics.push(metric);
        // 重新渲染
    }
    
    updateMetric(index, newData) {
        if (this.options.metrics[index]) {
            this.options.metrics[index] = { ...this.options.metrics[index], ...newData };
            // 重新渲染特定卡片
        }
    }
}

// 指标卡片样式
const metricsStyles = `
<style>
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--gray-200);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.metric-card.clickable {
    cursor: pointer;
}

.metric-card.clickable:hover {
    border-color: var(--primary);
}

.metric-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.metric-icon {
    width: 3rem;
    height: 3rem;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.metric-icon.primary {
    background-color: var(--primary-100);
    color: var(--primary);
}

.metric-icon.success {
    background-color: var(--success-light);
    color: var(--success);
}

.metric-icon.warning {
    background-color: var(--warning-light);
    color: var(--warning);
}

.metric-icon.error {
    background-color: var(--error-light);
    color: var(--error);
}

.metric-icon.info {
    background-color: var(--info-light);
    color: var(--info);
}

.metric-emoji {
    font-size: 2rem;
}

.metric-content {
    margin-bottom: 1rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--gray-900);
    margin: 0 0 0.25rem 0;
    line-height: 1;
}

.metric-title {
    font-size: 0.875rem;
    color: var(--gray-600);
    margin: 0;
    font-weight: 500;
}

.metric-subtitle {
    font-size: 0.75rem;
    color: var(--gray-500);
    margin: 0.25rem 0 0 0;
}

.metric-footer {
    margin-top: auto;
}

.metric-trend {
    display: flex;
    align-items: center;
    font-size: 0.875rem;
    font-weight: 500;
}

.metric-trend i {
    margin-right: 0.25rem;
}

.metric-trend.up {
    color: var(--success);
}

.metric-trend.down {
    color: var(--error);
}

.metric-trend.neutral {
    color: var(--gray-500);
}

.metric-progress {
    margin-top: 0.75rem;
}

.metric-progress .progress {
    margin-bottom: 0.5rem;
}

.progress-label {
    font-size: 0.75rem;
    color: var(--gray-500);
}

/* 响应式设计 */
@media (max-width: 1024px) {
    .metrics-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .metrics-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .metric-card {
        padding: 1rem;
    }
    
    .metric-value {
        font-size: 1.75rem;
    }
    
    .metric-icon {
        width: 2.5rem;
        height: 2.5rem;
        font-size: 1rem;
    }
}

/* 动画效果 */
@keyframes countUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.metric-card {
    animation: countUp 0.6s ease-out;
}

.metric-card:nth-child(2) {
    animation-delay: 0.1s;
}

.metric-card:nth-child(3) {
    animation-delay: 0.2s;
}

.metric-card:nth-child(4) {
    animation-delay: 0.3s;
}
</style>
`;

// 导出组件
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MetricCard, MetricsGrid, metricsStyles };
} else if (typeof window !== 'undefined') {
    window.MetricCard = MetricCard;
    window.MetricsGrid = MetricsGrid;
    window.metricsStyles = metricsStyles;
}
