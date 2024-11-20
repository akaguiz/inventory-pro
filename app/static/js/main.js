        // Add active state to current nav item
        document.addEventListener('DOMContentLoaded', function() {
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('nav a');
            
            navLinks.forEach(link => {
                if (link.getAttribute('href') === currentPath) {
                    link.classList.add('bg-gray-800/50');
                    const icon = link.querySelector('.w-10');
                    if (icon) {
                        icon.classList.remove('bg-gray-800');
                        icon.classList.add('gradient-bg');
                    }
                }
            });

            // Initialize tooltips, dropdowns, etc.
            setupNotifications();
        });

        // Setup notifications
        function setupNotifications() {
            const notificationBtn = document.querySelector('.fa-bell').parentElement;
            notificationBtn.addEventListener('click', () => {
                // Add notification panel logic here
                console.log('Notifications clicked');
            });
        }

        // Add smooth scroll behavior
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });