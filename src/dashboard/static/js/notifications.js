// static/js/notifications.js
class NotificationManager {
    show(title, message, type = 'info') {
        const container = document.getElementById('notificationArea');
        const notification = document.createElement('div');
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };

        notification.className = `${colors[type]} text-white p-4 rounded-lg shadow-lg mb-4 transform transition-all duration-300 opacity-0`;
        notification.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-semibold">${title}</h4>
                    <p class="text-sm">${message}</p>
                </div>
                <button class="ml-4 text-white hover:text-gray-200">&times;</button>
            </div>
        `;

        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('opacity-0');
        }, 10);

        // Setup close button
        const closeBtn = notification.querySelector('button');
        closeBtn.addEventListener('click', () => {
            notification.classList.add('opacity-0');
            setTimeout(() => {
                container.removeChild(notification);
            }, 300);
        });

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode === container) {
                notification.classList.add('opacity-0');
                setTimeout(() => {
                    if (notification.parentNode === container) {
                        container.removeChild(notification);
                    }
                }, 300);
            }
        }, 5000);
    }
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SecurityDashboard();
});