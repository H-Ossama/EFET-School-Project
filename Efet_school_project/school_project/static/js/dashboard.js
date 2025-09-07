// Modern Dashboard JavaScript
class DashboardManager {
    constructor() {
        this.sidebarCollapsed = false;
        this.currentSection = 'dashboard-overview';
        this.animationDelay = 100;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        this.checkResponsive();
        this.loadSavedState();
    }

    setupEventListeners() {
        // Sidebar toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('.sidebar-toggle, .mobile-menu-btn')) {
                this.toggleSidebar();
            }
        });

        // Menu navigation
        document.addEventListener('click', (e) => {
            const menuLink = e.target.closest('[onclick*="showSection"]');
            if (menuLink) {
                e.preventDefault();
                const sectionId = menuLink.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.showSection(sectionId);
            }
        });

        // Modal handling
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-overlay')) {
                this.closeModal(e.target);
            }
            
            if (e.target.matches('.modal-close')) {
                this.closeModal(e.target.closest('.modal-overlay'));
            }
        });

        // Search functionality
        document.addEventListener('input', (e) => {
            if (e.target.id === 'studentSearch') {
                this.searchTable('studentsTable', e.target.value);
            }
        });

        // Form submissions with loading states
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.modal-form')) {
                this.handleFormSubmission(e);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.checkResponsive();
        });

        // Touch events for mobile
        this.setupMobileGestures();

        // Scroll animations
        window.addEventListener('scroll', () => {
            this.handleScrollAnimations();
        });
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const dashboard = document.getElementById('dashboard');
        
        if (!sidebar) return;
        
        try {
            // Handle mobile differently
            if (window.innerWidth <= 768) {
                // Mobile behavior - use mobile-open class
                const isOpen = sidebar.classList.contains('mobile-open');
                
                if (isOpen) {
                    // Close sidebar
                    sidebar.classList.remove('mobile-open');
                    this.sidebarCollapsed = true;
                } else {
                    // Open sidebar
                    sidebar.classList.add('mobile-open');
                    this.sidebarCollapsed = false;
                }
                
                // Handle overlay
                let overlay = document.querySelector('.sidebar-overlay');
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.className = 'sidebar-overlay';
                    overlay.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.closeMobileSidebar();
                    });
                    document.body.appendChild(overlay);
                }
                
                // Explicitly set active state based on sidebar state
                if (!this.sidebarCollapsed) {
                    overlay.classList.add('active');
                } else {
                    overlay.classList.remove('active');
                }
                
                // Prevent body scroll when sidebar is open
                document.body.style.overflow = this.sidebarCollapsed ? '' : 'hidden';
            } else {
                // Desktop behavior - use collapsed class
                this.sidebarCollapsed = !this.sidebarCollapsed;
                sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
                dashboard.classList.toggle('sidebar-collapsed', this.sidebarCollapsed);
            }
            
            // Save state
            localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
            
            // Trigger animation
            this.triggerSidebarAnimation();
        } catch (error) {
            console.error('Error in toggleSidebar:', error);
            // Recovery code to ensure UI doesn't get stuck
            this.recoverFromSidebarError();
        }
    }

    closeMobileSidebar() {
        try {
            if (window.innerWidth <= 768) {
                const sidebar = document.getElementById('sidebar');
                const overlay = document.querySelector('.sidebar-overlay');
                
                if (sidebar) {
                    sidebar.classList.remove('mobile-open');
                }
                
                if (overlay) {
                    overlay.classList.remove('active');
                }
                
                document.body.style.overflow = '';
                this.sidebarCollapsed = true;
                localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
            }
        } catch (error) {
            console.error('Error in closeMobileSidebar:', error);
            this.recoverFromSidebarError();
        }
    }
    
    recoverFromSidebarError() {
        // Emergency recovery if sidebar gets stuck
        try {
            // Reset sidebar state
            this.sidebarCollapsed = true;
            localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
            
            // Reset body scroll
            document.body.style.overflow = '';
            
            // Remove overlay if exists
            const overlay = document.querySelector('.sidebar-overlay');
            if (overlay) {
                overlay.classList.remove('active');
            }
            
            // Reset sidebar if exists
            const sidebar = document.getElementById('sidebar');
            if (sidebar) {
                sidebar.classList.remove('mobile-open');
            }
            
            // Add emergency reset class to body
            document.body.classList.add('emergency-reset');
            
            // Show hint to user
            this.showEmergencyHint();
            
            // Remove emergency class after a delay
            setTimeout(() => {
                document.body.classList.remove('emergency-reset');
            }, 1000);
        } catch (finalError) {
            console.error('Critical error in sidebar recovery:', finalError);
        }
    }
    
    showEmergencyHint() {
        // Create hint element if it doesn't exist
        let hintElement = document.querySelector('.double-tap-escape-hint');
        if (!hintElement) {
            hintElement = document.createElement('div');
            hintElement.className = 'double-tap-escape-hint';
            hintElement.innerHTML = '<i class="fas fa-info-circle"></i> Double-tap ESC anytime to reset the interface';
            document.body.appendChild(hintElement);
        }
        
        // Show hint
        setTimeout(() => {
            hintElement.classList.add('show');
            
            // Hide after 3 seconds
            setTimeout(() => {
                hintElement.classList.remove('show');
            }, 3000);
        }, 300);
    }

    triggerSidebarAnimation() {
        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.transform = 'translateX(10px)';
                setTimeout(() => {
                    item.style.transform = '';
                }, 150);
            }, index * 50);
        });
    }

    showSection(sectionId) {
        // Hide all sections with fade out
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Remove active class from all menu items
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Show selected section with fade in
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            setTimeout(() => {
                targetSection.classList.add('active');
                this.animateSection(targetSection);
            }, 150);
        }
        
        // Add active class to corresponding menu item
        const menuLink = document.querySelector(`[onclick*="${sectionId}"]`);
        if (menuLink) {
            menuLink.closest('.menu-item').classList.add('active');
        }
        
        this.currentSection = sectionId;
        
        // Update page title with animation
        this.updatePageTitle(sectionId);
        
        // Save current section
        localStorage.setItem('currentSection', sectionId);
    }

    updatePageTitle(sectionId) {
        const pageTitles = {
            'dashboard-overview': 'Tableau de Bord',
            'students-section': 'Gestion des Étudiants',
            'teachers-section': 'Gestion des Enseignants',
            'majors-section': 'Gestion des Filières',
            'subjects-section': 'Gestion des Matières',
            'messages-section': 'Messages',
            'notifications-section': 'Notifications'
        };
        
        const titleElement = document.querySelector('.page-title');
        if (titleElement) {
            titleElement.style.opacity = '0';
            setTimeout(() => {
                titleElement.textContent = pageTitles[sectionId] || 'Tableau de Bord';
                titleElement.style.opacity = '1';
            }, 150);
        }
    }

    animateSection(section) {
        const cards = section.querySelectorAll('.stat-card, .dashboard-card, .major-card, .subject-card, .data-table-container');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.4s ease-out';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * this.animationDelay);
        });
    }

    toggleModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            if (modal.classList.contains('active')) {
                this.closeModal(modal);
            } else {
                this.openModal(modal);
            }
        }
    }

    openModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        setTimeout(() => {
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        }, 300);
        
        // Add opening animation
        const container = modal.querySelector('.modal-container');
        if (container) {
            container.style.transform = 'scale(0.9)';
            setTimeout(() => {
                container.style.transform = 'scale(1)';
            }, 50);
        }
    }

    closeModal(modal) {
        const container = modal.querySelector('.modal-container');
        if (container) {
            container.style.transform = 'scale(0.95)';
        }
        
        setTimeout(() => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            
            // Reset form if exists
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
            }
        }, 200);
    }

    searchTable(tableId, searchTerm) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        const filter = searchTerm.toUpperCase();
        
        rows.forEach(row => {
            let found = false;
            const cells = row.querySelectorAll('td');
            
            // Skip action column (last column)
            for (let i = 0; i < cells.length - 1; i++) {
                const text = cells[i].textContent || cells[i].innerText;
                if (text.toUpperCase().includes(filter)) {
                    found = true;
                    break;
                }
            }
            
            // Animate row visibility
            if (found) {
                row.style.display = '';
                row.style.opacity = '0';
                setTimeout(() => {
                    row.style.opacity = '1';
                }, 50);
            } else {
                row.style.opacity = '0';
                setTimeout(() => {
                    row.style.display = 'none';
                }, 200);
            }
        });
        
        // Show no results message if needed
        this.showNoResultsMessage(tableId, rows, filter);
    }

    showNoResultsMessage(tableId, rows, filter) {
        const table = document.getElementById(tableId);
        const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
        
        let noResultsRow = table.querySelector('.no-results-row');
        
        if (visibleRows.length === 0 && filter) {
            if (!noResultsRow) {
                const tbody = table.querySelector('tbody');
                const colCount = table.querySelectorAll('thead th').length;
                
                noResultsRow = document.createElement('tr');
                noResultsRow.className = 'no-results-row';
                noResultsRow.innerHTML = `
                    <td colspan="${colCount}" style="text-align: center; padding: 2rem; color: var(--gray-500);">
                        <i class="fas fa-search" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                        <div>Aucun résultat trouvé pour "${filter}"</div>
                    </td>
                `;
                tbody.appendChild(noResultsRow);
            }
        } else if (noResultsRow) {
            noResultsRow.remove();
        }
    }

    handleFormSubmission(e) {
        const form = e.target;
        const submitBtn = form.querySelector('[type="submit"]');
        
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Envoi...';
            submitBtn.disabled = true;
            
            // Reset button after 3 seconds (in case of errors)
            setTimeout(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 3000);
        }
    }

    handleKeyboardShortcuts(e) {
        // ESC to close modals
        if (e.key === 'Escape') {
            // First try to close any active modal
            const activeModal = document.querySelector('.modal-overlay.active');
            if (activeModal) {
                this.closeModal(activeModal);
                return; // Exit to prevent also closing sidebar
            }
            
            // Then try to close mobile sidebar if open
            if (window.innerWidth <= 768 && !this.sidebarCollapsed) {
                this.closeMobileSidebar();
                return;
            }
        }
        
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('studentSearch');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Number keys for quick navigation
        if (e.altKey && e.key >= '1' && e.key <= '7') {
            e.preventDefault();
            const sections = [
                'dashboard-overview',
                'students-section',
                'teachers-section',
                'majors-section',
                'subjects-section',
                'messages-section',
                'notifications-section'
            ];
            const index = parseInt(e.key) - 1;
            if (sections[index]) {
                this.showSection(sections[index]);
            }
        }
    }

    checkResponsive() {
        const isMobile = window.innerWidth <= 768;
        const isTablet = window.innerWidth <= 1024;
        
        // Handle mobile sidebar behavior
        if (isMobile) {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            
            // Always start with sidebar closed on mobile
            if (!this.sidebarCollapsed) {
                this.closeMobileSidebar();
            }
            
            // Ensure sidebar has proper mobile classes
            sidebar.classList.remove('collapsed');
            
            // Clean up any desktop-specific styles
            const dashboard = document.getElementById('dashboard');
            dashboard.classList.remove('sidebar-collapsed');
        } else {
            // Desktop/tablet behavior
            const sidebar = document.getElementById('sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            
            // Remove mobile classes
            sidebar.classList.remove('mobile-open');
            if (overlay) {
                overlay.remove();
            }
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            // Apply desktop sidebar state
            if (this.sidebarCollapsed) {
                sidebar.classList.add('collapsed');
                document.getElementById('dashboard').classList.add('sidebar-collapsed');
            }
        }
        
        // Adjust grid layouts
        this.adjustGridLayouts();
        
        // Adjust table scrolling
        this.adjustMobileTableScrolling();
    }

    adjustMobileTableScrolling() {
        if (window.innerWidth <= 768) {
            const tableContainers = document.querySelectorAll('.data-table-container');
            tableContainers.forEach(container => {
                // Add touch scrolling indicator
                container.addEventListener('scroll', (e) => {
                    const scrollLeft = e.target.scrollLeft;
                    const maxScroll = e.target.scrollWidth - e.target.clientWidth;
                    
                    // Add visual feedback for scrollable content
                    if (scrollLeft > 0) {
                        container.classList.add('scrolled-left');
                    } else {
                        container.classList.remove('scrolled-left');
                    }
                    
                    if (scrollLeft < maxScroll - 1) {
                        container.classList.add('scrollable-right');
                    } else {
                        container.classList.remove('scrollable-right');
                    }
                });
                
                // Initial check
                if (container.scrollWidth > container.clientWidth) {
                    container.classList.add('scrollable-right');
                }
            });
        }
    }

    setupMobileGestures() {
        if (window.innerWidth <= 768) {
            let startX = 0;
            let startY = 0;
            
            // Swipe to open/close sidebar
            document.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            }, { passive: true });
            
            document.addEventListener('touchmove', (e) => {
                if (!startX || !startY) return;
                
                const currentX = e.touches[0].clientX;
                const currentY = e.touches[0].clientY;
                
                const diffX = startX - currentX;
                const diffY = startY - currentY;
                
                // Only handle horizontal swipes
                if (Math.abs(diffX) > Math.abs(diffY)) {
                    // Swipe from left edge to open sidebar
                    if (startX < 50 && diffX < -50 && this.sidebarCollapsed) {
                        this.toggleSidebar();
                    }
                    // Swipe left to close sidebar
                    else if (diffX > 50 && !this.sidebarCollapsed) {
                        this.closeMobileSidebar();
                    }
                }
                
                startX = 0;
                startY = 0;
            }, { passive: true });
        }
    }

    adjustGridLayouts() {
        const grids = document.querySelectorAll('.stats-grid, .dashboard-grid, .majors-grid, .subjects-grid');
        const isTablet = window.innerWidth <= 1024;
        const isMobile = window.innerWidth <= 768;
        
        grids.forEach(grid => {
            if (isMobile) {
                grid.style.gridTemplateColumns = '1fr';
            } else if (isTablet) {
                grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(250px, 1fr))';
            } else {
                grid.style.gridTemplateColumns = '';
            }
        });
    }

    handleScrollAnimations() {
        const elements = document.querySelectorAll('.fade-in-up:not(.active)');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    }

    initializeAnimations() {
        // Add fade-in-up class to animatable elements
        const elements = document.querySelectorAll('.stat-card, .dashboard-card, .major-card, .subject-card');
        elements.forEach(element => {
            element.classList.add('fade-in-up');
        });
        
        // Trigger initial animations
        setTimeout(() => {
            this.handleScrollAnimations();
        }, 500);
    }

    loadSavedState() {
        // Load sidebar state
        const savedSidebarState = localStorage.getItem('sidebarCollapsed');
        if (savedSidebarState === 'true' && !this.sidebarCollapsed) {
            this.toggleSidebar();
        }
        
        // Load current section
        const savedSection = localStorage.getItem('currentSection');
        if (savedSection && savedSection !== this.currentSection) {
            this.showSection(savedSection);
        }
    }

    // CRUD Operations with enhanced UX
    editStudent(studentId) {
        // Don't override the global editStudent function from dashboard.html
        if (window.originalEditStudent) {
            window.originalEditStudent(studentId);
        } else {
            // Fallback if the original function isn't available
            fetch(`/get_student_data/${studentId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const student = data.student;
                        // Populate form and show modal logic would go here
                        document.getElementById('edit_user_id').value = student.id;
                        document.getElementById('edit_name').value = student.name || '';
                        document.getElementById('edit_email').value = student.email || '';
                        // ... populate other fields ...
                        toggleModal('editStudentModal');
                    }
                });
        }
    }

    deleteStudent(studentId) {
        this.showConfirmDialog(
            'Supprimer l\'étudiant',
            'Êtes-vous sûr de vouloir supprimer cet étudiant ? Cette action est irréversible.',
            () => {
                this.performDelete('/deleteStudent', { user_id: studentId });
            }
        );
    }

    editTeacher(teacherId) {
        // Don't override the global editTeacher function from dashboard.html
        if (window.originalEditTeacher) {
            window.originalEditTeacher(teacherId);
        } else {
            // If no proper implementation exists, let's alert the user
            this.showNotification('La fonction d\'édition des enseignants est en cours de développement.', 'info');
        }
    }

    deleteTeacher(teacherId) {
        this.showConfirmDialog(
            'Supprimer l\'enseignant',
            'Êtes-vous sûr de vouloir supprimer cet enseignant ? Cette action est irréversible.',
            () => {
                this.performDelete('/deleteStudent', { user_id: teacherId });
            }
        );
    }

    editMajor(majorId) {
        this.showLoadingSpinner();
        
        setTimeout(() => {
            this.hideLoadingSpinner();
            this.showNotification('Fonction d\'édition sera bientôt disponible', 'info');
        }, 1000);
    }

    deleteMajor(majorId) {
        this.showConfirmDialog(
            'Supprimer la filière',
            'Êtes-vous sûr de vouloir supprimer cette filière ? Cette action est irréversible.',
            () => {
                this.performDelete('/deleteMajor', { major_id: majorId });
            }
        );
    }

    editSubject(subjectId) {
        this.showLoadingSpinner();
        
        setTimeout(() => {
            this.hideLoadingSpinner();
            this.showNotification('Fonction d\'édition sera bientôt disponible', 'info');
        }, 1000);
    }

    deleteSubject(subjectId) {
        this.showConfirmDialog(
            'Supprimer la matière',
            'Êtes-vous sûr de vouloir supprimer cette matière ? Cette action est irréversible.',
            () => {
                this.performDelete('/deleteSubject', { subject_id: subjectId });
            }
        );
    }

    performDelete(action, data) {
        this.showLoadingSpinner();
        
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = action;
        
        Object.keys(data).forEach(key => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = data[key];
            form.appendChild(input);
        });
        
        document.body.appendChild(form);
        form.submit();
    }

    showConfirmDialog(title, message, onConfirm) {
        // Create and show custom confirm dialog
        const dialog = document.createElement('div');
        dialog.className = 'modal-overlay active';
        dialog.innerHTML = `
            <div class="modal-container small">
                <div class="modal-header">
                    <h3>${title}</h3>
                </div>
                <div style="padding: 1.5rem;">
                    <p style="margin-bottom: 1.5rem; color: var(--gray-700);">${message}</p>
                    <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                        <button class="btn-secondary cancel-btn">Annuler</button>
                        <button class="btn-primary confirm-btn" style="background: var(--error-color);">
                            <i class="fas fa-trash"></i>
                            Supprimer
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        document.body.style.overflow = 'hidden';
        
        // Handle buttons
        dialog.querySelector('.cancel-btn').addEventListener('click', () => {
            this.closeModal(dialog);
            dialog.remove();
        });
        
        dialog.querySelector('.confirm-btn').addEventListener('click', () => {
            this.closeModal(dialog);
            dialog.remove();
            onConfirm();
        });
        
        // Close on overlay click
        dialog.addEventListener('click', (e) => {
            if (e.target === dialog) {
                this.closeModal(dialog);
                dialog.remove();
            }
        });
    }

    showLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.id = 'loading-spinner';
        spinner.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                backdrop-filter: blur(4px);
            ">
                <div style="
                    background: white;
                    padding: 2rem;
                    border-radius: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                ">
                    <i class="fas fa-spinner fa-spin" style="font-size: 1.5rem; color: var(--primary-color);"></i>
                    <span style="color: var(--gray-700); font-weight: 500;">Chargement...</span>
                </div>
            </div>
        `;
        document.body.appendChild(spinner);
    }

    hideLoadingSpinner() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = 'notification-toast';
        
        const colors = {
            success: 'var(--success-color)',
            error: 'var(--error-color)',
            warning: 'var(--warning-color)',
            info: 'var(--primary-color)'
        };
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <div style="
                position: fixed;
                top: 2rem;
                right: 2rem;
                background: white;
                padding: 1rem 1.5rem;
                border-radius: 0.75rem;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                border-left: 4px solid ${colors[type]};
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                max-width: 400px;
                transform: translateX(100%);
                transition: transform 0.3s ease-in-out;
            ">
                <i class="${icons[type]}" style="color: ${colors[type]};"></i>
                <span style="color: var(--gray-700);">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: var(--gray-500);
                    cursor: pointer;
                    margin-left: auto;
                ">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.firstElementChild.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.firstElementChild.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    exportData(type) {
        this.showLoadingSpinner();
        
        setTimeout(() => {
            this.hideLoadingSpinner();
            this.showNotification('Export sera bientôt disponible', 'info');
        }, 1500);
    }

    toggleNotifications() {
        this.showSection('notifications-section');
    }

    toggleUserMenu() {
        this.showNotification('Menu utilisateur sera bientôt disponible', 'info');
    }

    markAsRead(notificationId) {
        const notificationCard = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (notificationCard) {
            notificationCard.classList.remove('unread');
            this.showNotification('Notification marquée comme lue', 'success');
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
    
    // Make functions globally available for onclick handlers
    window.toggleSidebar = () => window.dashboardManager.toggleSidebar();
    window.showSection = (sectionId) => window.dashboardManager.showSection(sectionId);
    window.toggleModal = (modalId) => window.dashboardManager.toggleModal(modalId);
    window.closeMobileSidebar = () => window.dashboardManager.closeMobileSidebar();
    window.searchStudents = () => {
        const input = document.getElementById('studentSearch');
        if (input) {
            window.dashboardManager.searchTable('studentsTable', input.value);
        }
    };
    
    // CRUD functions
    // Don't override the existing editStudent function that uses originalEditStudent
    // window.editStudent = (id) => window.dashboardManager.editStudent(id);
    window.deleteStudent = (id) => window.dashboardManager.deleteStudent(id);
    // Don't override the existing editTeacher function that uses originalEditTeacher
    // window.editTeacher = (id) => window.dashboardManager.editTeacher(id);
    window.deleteTeacher = (id) => window.dashboardManager.deleteTeacher(id);
    window.editMajor = (id) => window.dashboardManager.editMajor(id);
    window.deleteMajor = (id) => window.dashboardManager.deleteMajor(id);
    window.editSubject = (id) => window.dashboardManager.editSubject(id);
    window.deleteSubject = (id) => window.dashboardManager.deleteSubject(id);
    window.exportData = (type) => window.dashboardManager.exportData(type);
    window.toggleNotifications = () => window.dashboardManager.toggleNotifications();
    window.toggleUserMenu = () => window.dashboardManager.toggleUserMenu();
    window.markAsRead = (id) => window.dashboardManager.markAsRead(id);
    
    // Add emergency escape key - double tap Escape to close sidebar and reset UI
    let escapeKeyPressTime = 0;
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const currentTime = new Date().getTime();
            if (currentTime - escapeKeyPressTime < 500) {
                // Double tap detected - emergency reset
                try {
                    // Add emergency reset class
                    document.body.classList.add('emergency-reset');
                    
                    const sidebar = document.getElementById('sidebar');
                    const overlay = document.querySelector('.sidebar-overlay');
                    
                    // Reset sidebar
                    if (sidebar) {
                        sidebar.classList.remove('mobile-open');
                        sidebar.classList.remove('active');
                    }
                    
                    // Remove overlay
                    if (overlay) {
                        overlay.classList.remove('active');
                        overlay.style.display = 'none';
                    }
                    
                    // Reset body
                    document.body.style.overflow = '';
                    
                    // Reset modals
                    document.querySelectorAll('.modal-overlay').forEach(modal => {
                        modal.classList.remove('active');
                    });
                    
                    // Show hint
                    if (window.dashboardManager) {
                        window.dashboardManager.showEmergencyHint();
                    }
                    
                    console.log('Emergency UI reset performed');
                    
                    // Remove emergency class after a delay
                    setTimeout(() => {
                        document.body.classList.remove('emergency-reset');
                    }, 1000);
                } catch (error) {
                    console.error('Error during emergency reset:', error);
                    // Last resort - reload the page if all else fails
                    if (confirm('Interface appears to be stuck. Reload the page?')) {
                        window.location.reload();
                    }
                }
            }
            escapeKeyPressTime = currentTime;
        }
    });
    
    // Prevent horizontal scrolling on mobile by handling touch events
    if ('ontouchstart' in window) {
        document.addEventListener('touchmove', function(e) {
            // If we're not in a scrollable element, prevent horizontal scrolling
            if (!isInScrollableArea(e.target)) {
                // If the movement is more horizontal than vertical
                if (Math.abs(e.touches[0].clientX - lastTouchX) > 
                    Math.abs(e.touches[0].clientY - lastTouchY)) {
                    e.preventDefault();
                }
            }
        }, { passive: false });
        
        // Track touch start positions
        let lastTouchX = 0;
        let lastTouchY = 0;
        document.addEventListener('touchstart', function(e) {
            lastTouchX = e.touches[0].clientX;
            lastTouchY = e.touches[0].clientY;
        }, { passive: true });
        
        // Function to check if we're in a horizontally scrollable area
        function isInScrollableArea(element) {
            // Check if we're in a table or data-table-container which should scroll horizontally
            while (element && element !== document.body) {
                if (element.classList.contains('data-table-container') || 
                    element.tagName === 'TABLE') {
                    return true;
                }
                element = element.parentElement;
            }
            return false;
        }
    }
});