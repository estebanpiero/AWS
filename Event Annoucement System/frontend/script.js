// Event Announcement System - Frontend JavaScript
// Replace YOUR_API_GATEWAY_URL with your actual API Gateway URL
// Format: https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication before loading events
    if (!localStorage.getItem('accessToken')) {
        window.location.href = 'login.html';
        return;
    }

    const eventsContainer = document.getElementById('eventsContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const calendarContainer = document.getElementById('calendarContainer');
    const noEventsMessage = document.getElementById('noEventsMessage');

    let allEvents = [];
    let currentDate = new Date();
    let currentFilter = 'all';

    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    // Load events immediately
    loadEvents();

    // Add filter functionality
    document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            filterAndDisplayEvents();
        });
    });

    // Add search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterAndDisplayEvents);
    }

    async function loadEvents() {
        // Check authentication before loading events
        if (!localStorage.getItem('accessToken')) {
            window.location.href = 'login.html';
            return;
        }

        try {
            showLoading();

            // REPLACE THIS URL WITH YOUR API GATEWAY URL
            const response = await fetch('YOUR_API_GATEWAY_URL/events');  // Replace YOUR_API_GATEWAY_URL

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const events = await response.json();

            allEvents = Array.isArray(events) ? events : [];
            allEvents.sort((a, b) => new Date(a.date || a.event_date) - new Date(b.date || b.event_date));

            filterAndDisplayEvents();

        } catch (error) {
            hideLoading();
            eventsContainer.innerHTML = '<p>Error loading events: ' + error.message + '</p>';
        }
    }

    function showLoading() {
        if (loadingIndicator) loadingIndicator.style.display = 'block';
        if (eventsContainer) eventsContainer.style.display = 'none';
        if (calendarContainer) calendarContainer.style.display = 'none';
        if (noEventsMessage) noEventsMessage.style.display = 'none';
    }

    function hideLoading() {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (calendarContainer) calendarContainer.style.display = 'block';
        if (eventsContainer) eventsContainer.style.display = 'grid';
    }

    function filterAndDisplayEvents() {
        const searchInput = document.getElementById('searchInput');
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';

        let filtered = [...allEvents];

        // Apply search filter
        if (searchTerm) {
            filtered = filtered.filter(event =>
                (event.title && event.title.toLowerCase().includes(searchTerm)) ||
                (event.description && event.description.toLowerCase().includes(searchTerm)) ||
                (event.address && event.address.toLowerCase().includes(searchTerm))
            );
        }

        // Apply date filter
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (currentFilter === 'upcoming') {
            filtered = filtered.filter(event => {
                const eventDate = new Date(event.date || event.event_date);
                eventDate.setHours(0, 0, 0, 0);
                return eventDate >= today;
            });
        } else if (currentFilter === 'today') {
            filtered = filtered.filter(event => {
                const eventDate = new Date(event.date || event.event_date);
                eventDate.setHours(0, 0, 0, 0);
                return eventDate.getTime() === today.getTime();
            });
        }

        displayEvents(filtered);
        renderCalendar();
    }

    function displayEvents(events) {
        hideLoading();

        if (!eventsContainer) return;

        if (events.length === 0) {
            eventsContainer.style.display = 'none';
            if (noEventsMessage) noEventsMessage.style.display = 'block';
            return;
        }

        if (noEventsMessage) noEventsMessage.style.display = 'none';
        eventsContainer.style.display = 'grid';

        const html = events.map(event => {
            const eventDate = new Date(event.date || event.event_date);
            const formattedDate = eventDate.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            const formattedTime = eventDate.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });

            return `
                <div class="event-card" id="event-${event.event_id}">
                    <div class="event-header">
                        <h3>${escapeHtml(event.title)}</h3>
                        <button class="delete-btn" onclick="deleteEvent('${event.event_id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div class="event-content">
                        <div class="event-meta">
                            <span><i class="fas fa-calendar"></i> ${formattedDate}</span>
                            <span><i class="fas fa-clock"></i> ${formattedTime}</span>
                            ${event.address ? `<span><i class="fas fa-map-marker-alt"></i> ${escapeHtml(event.address)}</span>` : ''}
                            ${event.created_by_name && event.created_by_name !== 'Anonymous User' ? `<span><i class="fas fa-user"></i> Created by ${escapeHtml(event.created_by_name)}</span>` : ''}
                        </div>
                        <p class="event-description">${escapeHtml(event.description)}</p>
                        <div class="calendar-buttons">
                            <button class="calendar-btn google-cal" onclick="addToGoogleCalendar('${event.event_id}')">
                                <i class="fab fa-google"></i> Google Calendar
                            </button>
                            <button class="calendar-btn apple-cal" onclick="addToAppleCalendar('${event.event_id}')">
                                <i class="fab fa-apple"></i> Apple Calendar
                            </button>
                        </div>
                        ${event.address ? `
                            <div class="map-container">
                                <iframe width="100%" height="200" frameborder="0" style="border:0;"
                                    src="https://maps.google.com/maps?q=${encodeURIComponent(event.address)}&output=embed"
                                    allowfullscreen>
                                </iframe>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        if (eventsContainer) eventsContainer.innerHTML = html;
    }

    function renderCalendar() {
        const calendar = document.getElementById('calendar');
        const calendarTitle = document.getElementById('calendarTitle');

        if (!calendar || !calendarTitle) return;

        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        calendarTitle.textContent = `${monthNames[month]} ${year}`;

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());

        calendar.innerHTML = '';

        // Add day headers
        dayNames.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'calendar-day-header';
            dayHeader.textContent = day;
            calendar.appendChild(dayHeader);
        });

        // Add calendar days
        for (let i = 0; i < 42; i++) {
            const currentDay = new Date(startDate);
            currentDay.setDate(startDate.getDate() + i);

            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';

            if (currentDay.getMonth() !== month) {
                dayElement.classList.add('other-month');
            }

            if (currentDay.toDateString() === new Date().toDateString()) {
                dayElement.classList.add('today');
            }

            // Check if there are events on this day
            const dayEvents = allEvents.filter(event => {
                const eventDate = new Date(event.date || event.event_date);
                return eventDate.toDateString() === currentDay.toDateString();
            });

            if (dayEvents.length > 0) {
                dayElement.classList.add('has-events');
                dayElement.title = `${dayEvents.length} event(s)`;
            }

            dayElement.innerHTML = `
                <span class="day-number">${currentDay.getDate()}</span>
                ${dayEvents.length > 0 ? `<span class="event-indicator">${dayEvents.length}</span>` : ''}
            `;

            calendar.appendChild(dayElement);
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    // Make changeMonth available globally
    window.changeMonth = function(direction) {
        currentDate.setMonth(currentDate.getMonth() + direction);
        renderCalendar();
    };

    // Delete event function
    window.deleteEvent = async function(eventId) {
        if (!confirm('Are you sure you want to delete this event?')) {
            return;
        }

        try {
            // REPLACE THIS URL WITH YOUR API GATEWAY URL
            const response = await fetch(`YOUR_API_GATEWAY_URL/events/${eventId}`, {  // Replace YOUR_API_GATEWAY_URL
                method: 'DELETE'
            });

            if (response.ok) {
                // Remove from local array and refresh display
                allEvents = allEvents.filter(event => event.event_id !== eventId);
                filterAndDisplayEvents();
            } else {
                alert('Failed to delete event');
            }
        } catch (error) {
            alert('Error deleting event');
        }
    };

    // Calendar integration functions
    window.addToGoogleCalendar = function(eventId) {
        const event = allEvents.find(e => e.event_id === eventId || e.id === eventId);
        if (!event) return;

        const startDate = new Date(event.date || event.event_date);
        const endDate = new Date(startDate.getTime() + 60 * 60 * 1000);

        const googleUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.title)}&dates=${formatDateForCalendar(startDate)}/${formatDateForCalendar(endDate)}&details=${encodeURIComponent(event.description)}&location=${encodeURIComponent(event.address || '')}`;

        window.open(googleUrl, '_blank');
    };

    window.addToAppleCalendar = function(eventId) {
        const event = allEvents.find(e => e.event_id === eventId || e.id === eventId);
        if (!event) return;

        const startDate = new Date(event.date || event.event_date);
        const endDate = new Date(startDate.getTime() + 60 * 60 * 1000);

        const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Event System//EN
BEGIN:VEVENT
UID:${eventId}@events.com
DTSTAMP:${formatDateForICS(new Date())}
DTSTART:${formatDateForICS(startDate)}
DTEND:${formatDateForICS(endDate)}
SUMMARY:${event.title}
DESCRIPTION:${event.description}
LOCATION:${event.address || ''}
END:VEVENT
END:VCALENDAR`;

        const blob = new Blob([icsContent], { type: 'text/calendar' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${event.title}.ics`;
        link.click();
        URL.revokeObjectURL(url);
    };

    function formatDateForCalendar(date) {
        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    }

    function formatDateForICS(date) {
        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    }
});
