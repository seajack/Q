// 侧边栏组件
class Sidebar {
    constructor(options = {}) {
        this.options = {
            logoSrc: '../logo.jpg',
            logoAlt: 'Logo',
            title: '绩效考核系统',
            subtitle: 'Performance System',
            user: {
                name: '管理员',
                email: 'admin@company.com',
                avatar: null
            },
            menuItems: [
                { id: 'dashboard', icon: 'fas fa-tachometer-alt', label: '仪表板', active: true },
                { id: 'cycles', icon: 'fas fa-calendar-alt', label: '考核周期' },
                { id: 'tasks', icon: 'fas fa-tasks', label: '考核任务' },
                { id: 'evaluation', icon: 'fas fa-star', label: '评分管理' },
                { id: 'results', icon: 'fas fa-chart-bar', label: '结果统计' },
                { id: 'employees', icon: 'fas fa-users', label: '员工管理' },
                { id: 'settings', icon: 'fas fa-cog', label: '系统设置' }
            ],
            ...options
        };
        
        this.currentActive = this.options.menuItems.find(item => item.active)?.id || 'dashboard';
        this.onMenuClick = options.onMenuClick || (() => {});
    }
    
    render() {
        return `
            <div class="sidebar-container">
                ${this.renderHeader()}
                ${this.renderNavigation()}
                ${this.renderUserInfo()}
            </div>
        `;
    }
    
    renderHeader() {
        return `
            <div class="sidebar-header">
                <div class="logo-container">
                    <img src="${this.options.logoSrc}" alt="${this.options.logoAlt}" class="logo-img">
                </div>
                <div class="title-container">
                    <h1 class="sidebar-title">${this.options.title}</h1>
                    <p class="sidebar-subtitle">${this.options.subtitle}</p>
                </div>
            </div>
        `;
    }
    
    renderNavigation() {
        const menuItems = this.options.menuItems.map(item => `
            <div class="nav-item ${item.active ? 'active' : ''}" data-menu-id="${item.id}">
                <i class="${item.icon}"></i>
                <span>${item.label}</span>
            </div>
        `).join('');
        
        return `
            <nav class="sidebar-nav">
                ${menuItems}
            </nav>
        `;
    }
    
    renderUserInfo() {
        const { user } = this.options;
        const avatarContent = user.avatar 
            ? `<img src="${user.avatar}" alt="${user.name}" class="user-avatar-img">`
            : `<i class="fas fa-user"></i>`;
            
        return `
            <div class="sidebar-footer">
                <div class="user-info">
                    <div class="user-avatar">
                        ${avatarContent}
                    </div>
                    <div class="user-details">
                        <p class="user-name">${user.name}</p>
                        <p class="user-email">${user.email}</p>
                    </div>
                </div>
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
        const navItems = container.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const menuId = item.dataset.menuId;
                this.setActive(menuId);
                this.onMenuClick(menuId, item);
            });
        });
    }
    
    setActive(menuId) {
        // 更新内部状态
        this.options.menuItems.forEach(item => {
            item.active = item.id === menuId;
        });
        this.currentActive = menuId;
        
        // 更新DOM
        const container = document.querySelector('.sidebar-container');
        if (container) {
            const navItems = container.querySelectorAll('.nav-item');
            navItems.forEach(item => {
                if (item.dataset.menuId === menuId) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }
    }
    
    updateUser(userData) {
        this.options.user = { ...this.options.user, ...userData };
        const userInfo = document.querySelector('.user-info');
        if (userInfo) {
            userInfo.innerHTML = this.renderUserInfo().match(/<div class="user-info">(.*?)<\/div>/s)[1];
        }
    }
}

// 侧边栏样式
const sidebarStyles = `
<style>
.sidebar-container {
    width: 16rem;
    height: 100vh;
    background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    display: flex;
    flex-direction: column;
    padding: 1.5rem;
    border-right: 1px solid var(--gray-200);
}

.sidebar-header {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
}

.logo-container {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: var(--radius);
    overflow: hidden;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    padding: 0.125rem;
}

.logo-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.title-container {
    flex: 1;
}

.sidebar-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--gray-900);
    margin: 0;
}

.sidebar-subtitle {
    font-size: 0.875rem;
    color: var(--gray-500);
    margin: 0;
}

.sidebar-nav {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.nav-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    margin: 0.125rem 0;
    border-radius: var(--radius);
    color: var(--gray-700);
    cursor: pointer;
    transition: all 0.2s ease;
}

.nav-item:hover {
    background-color: var(--primary-100);
    color: var(--primary);
}

.nav-item.active {
    background-color: var(--primary);
    color: white;
}

.nav-item i {
    margin-right: 0.75rem;
    width: 1rem;
    text-align: center;
}

.sidebar-footer {
    margin-top: auto;
}

.user-info {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    background-color: var(--gray-200);
    border-radius: var(--radius);
}

.user-avatar {
    width: 2rem;
    height: 2rem;
    background-color: var(--primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    color: white;
    font-size: 0.875rem;
}

.user-avatar-img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}

.user-details {
    flex: 1;
}

.user-name {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--gray-900);
    margin: 0;
}

.user-email {
    font-size: 0.75rem;
    color: var(--gray-500);
    margin: 0;
}

@media (max-width: 768px) {
    .sidebar-container {
        width: 100%;
        height: auto;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .sidebar-container.open {
        transform: translateX(0);
    }
}
</style>
`;

// 导出组件
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Sidebar, sidebarStyles };
} else if (typeof window !== 'undefined') {
    window.Sidebar = Sidebar;
    window.sidebarStyles = sidebarStyles;
}
