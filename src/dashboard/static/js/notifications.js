class NotificationManager {
    constructor() {
        this.container = document.getElementById('notificationArea');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notificationArea';
            this.container.className = 'fixed bottom-4 right-4 w-80 z-50';
            document.body.appendChild(this.container);
        }
    }

    show(title, message, type = 'info') {
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

        this.container.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('opacity-0');
        }, 10);

        // Setup close button
        const closeBtn = notification.querySelector('button');
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });

        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeNotification(notification);
        }, 5000);
    }

    removeNotification(notification) {
        notification.classList.add('opacity-0');
        setTimeout(() => {
            if (notification.parentNode === this.container) {
                this.container.removeChild(notification);
            }
        }, 300);
    }
}