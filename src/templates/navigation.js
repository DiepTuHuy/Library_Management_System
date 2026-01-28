/**
 * Navigation Utility for Library Management System
 * Handles all navigation flows and role-based routing
 */

// Navigation Configuration
const navigationConfig = {
    admin: {
        overview: 'Overview.html',
        manageUser: 'ManageUser.html',
        manageBooks: 'ManageBook.html',
        addBook: 'AddBook.html',
        addUser: 'AddUser.html',
        reports: {
            base: 'ReportBorrow.html',
            borrow: 'ReportBorrow.html',
            category: 'ReportCategory.html',
            late: 'ReportLate.html',
            topBooks: 'ReportTopBook.html'
        }
    },
    librarian: {
        overview: 'Overview.html',
        manageBooks: 'ManageBooks.html',
        addBook: 'AddBook.html',
        addUser: 'AddUser.html',
        manageUser: 'ManageUser.html',
        borrowingBooks: 'BorrowingBooks.html',
        returning: 'Returning.html',
        checkinCard: 'CheckinCard.html',
        checkinDetail: 'CheckinDetail.html',
        reports: {
            base: 'ReportBorrow.html',
            borrow: 'ReportBorrow.html',
            category: 'ReportCategory.html',
            late: 'ReportLate.html',
            topBooks: 'ReportTopBook.html'
        }
    },
    member: {
        overview: 'Overview.html',
        myBooks: 'MyBook.html',
        searchBooks: 'SearchBook.html',
        history: 'History.html',
        bookDetail: 'BookDetail.html',
        borrowDetail: 'BorrowDetail.html',
        profile: 'Profile.html'
    },
    guest: {
        main: 'Guest.html',
        borrowDetail: 'BorrowDetail.html'
    }
};

/**
 * Navigate to a page within the same role dashboard
 * @param {string} role - Role (admin, librarian, member, guest)
 * @param {string} page - Page to navigate to
 */
function navigateToRolePage(role, page) {
    const config = navigationConfig[role];
    if (config && config[page]) {
        const path = config[page];
        window.location.href = path;
    } else {
        console.error(`Invalid navigation: role=${role}, page=${page}`);
    }
}

/**
 * Navigate to a report page
 * @param {string} role - Role (admin or librarian)
 * @param {string} reportType - Type of report (borrow, category, late, topBooks)
 */
function navigateToReport(role, reportType) {
    const config = navigationConfig[role];
    if (config && config.reports && config.reports[reportType]) {
        const path = config.reports[reportType];
        window.location.href = path;
    } else {
        console.error(`Invalid report: role=${role}, type=${reportType}`);
    }
}

/**
 * Logout function - return to login
 */
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '../Login.html';
    }
}

/**
 * Login handler - route to appropriate dashboard based on role
 * @param {string} role - User role (admin, librarian, member, guest)
 */
function loginRedirect(role) {
    const paths = {
        admin: 'Admin/Overview.html',
        librarian: 'Librarian/Overview.html',
        member: 'Member/Overview.html',
        guest: 'Guest/Guest.html'
    };
    
    if (paths[role]) {
        window.location.href = paths[role];
    }
}

/**
 * Set active navigation tab
 * @param {HTMLElement} tabElement - The tab element to activate
 */
function setActiveTab(tabElement) {
    // Remove active class from all tabs
    const allTabs = document.querySelectorAll('.nav-tab, .nav-link');
    allTabs.forEach(tab => tab.classList.remove('active'));
    
    // Add active class to clicked tab
    if (tabElement) {
        tabElement.classList.add('active');
    }
}

/**
 * Initialize navigation based on current page
 */
function initializeNavigation() {
    // Get current page filename
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Find and activate the corresponding nav item
    const navItems = document.querySelectorAll('[data-nav]');
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPage || href.includes(currentPage)) {
            item.classList.add('active');
        }
    });
}

/**
 * Create navigation for Admin dashboard
 */
function createAdminNav() {
    return `
        <nav class="nav-tabs">
            <a href="Overview.html" class="nav-tab active" data-nav>Overview</a>
            <a href="ManageUser.html" class="nav-tab" data-nav>Manage User</a>
            <a href="ManageBook.html" class="nav-tab" data-nav>Manage Books</a>
            <a href="ReportBorrow.html" class="nav-tab" data-nav>Reports</a>
        </nav>
    `;
}

/**
 * Create navigation for Librarian dashboard
 */
function createLibrarianNav() {
    return `
        <nav class="nav-tabs">
            <a href="Overview.html" class="nav-tab active" data-nav>Overview</a>
            <a href="AddBook.html" class="nav-tab" data-nav>Add Book</a>
            <a href="ManageBooks.html" class="nav-tab" data-nav>Manage Books</a>
            <a href="BorrowingBooks.html" class="nav-tab" data-nav>Borrowing Books</a>
            <a href="Returning.html" class="nav-tab" data-nav>Returning</a>
            <a href="AddUser.html" class="nav-tab" data-nav>Add User</a>
            <a href="ManageUser.html" class="nav-tab" data-nav>Manage User</a>
            <a href="ReportBorrow.html" class="nav-tab" data-nav>Reports</a>
        </nav>
    `;
}

/**
 * Create navigation for Member dashboard
 */
function createMemberNav() {
    return `
        <nav class="nav-tabs">
            <a href="Overview.html" class="nav-tab active" data-nav>Overview</a>
            <a href="MyBook.html" class="nav-tab" data-nav>My Books</a>
            <a href="SearchBook.html" class="nav-tab" data-nav>Search Books</a>
            <a href="History.html" class="nav-tab" data-nav>History</a>
            <a href="Profile.html" class="nav-tab" data-nav>Profile</a>
        </nav>
    `;
}

// Initialize navigation when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeNavigation);
} else {
    initializeNavigation();
}
