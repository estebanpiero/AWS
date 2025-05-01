const apiBaseUrl = "<API>";

document.addEventListener('DOMContentLoaded', function() {
    const eventsContainer = document.getElementById('events');
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    
    let allEvents = []; // Store all events for filtering

    async function loadEvents() {
        showLoading();
        try {
            const res = await fetch(apiBaseUrl, {
                method: "GET"
            });

            const data = await res.json();
            allEvents = JSON.parse(data.body);
            
            filterAndDisplayEvents();

        } catch (error) {
            console.error('Error loading events:', error);
            showError();
        }
    }

    function filterAndDisplayEvents() {
        let filteredEvents = [...allEvents];

        // Apply search filter
        const searchTerm = searchInput.value.toLowerCase();
        if (searchTerm) {
            filteredEvents = filteredEvents.filter(event => 
                event.title.toLowerCase().includes(searchTerm) ||
                event.description.toLowerCase().includes(searchTerm)
            );
        }

        // Apply sorting
        const sortValue = sortSelect.value;
        filteredEvents.sort((a, b) => {
            switch(sortValue) {
                case 'dateAsc':
                    return new Date(a.event_date || a.date) - new Date(b.event_date || b.date);
                case 'dateDesc':
                    return new Date(b.event_date || b.date) - new Date(a.event_date || a.date);
                case 'titleAsc':
                    return a.title.localeCompare(b.title);
                case 'titleDesc':
                    return b.title.localeCompare(a.title);
                default:
                    return 0;
            }
        });

        displayEvents(filteredEvents);
    }

    function showLoading() {
        eventsContainer.innerHTML = '<div class="loading">Loading events...</div>';
    }

    function showError() {
        eventsContainer.innerHTML = `
            <div class="no-events">
                <h3>Error Loading Events</h3>
                <p>Failed to load events. Please try again later.</p>
            </div>
        `;
    }

    function showNoEvents() {
        eventsContainer.innerHTML = `
            <div class="no-events">
                <h3>No Events Found</h3>
                <p>There are currently no scheduled events.</p>
            </div>
        `;
    }

    function displayEvents(events) {
        eventsContainer.innerHTML = "";

        if (!events.length) {
            showNoEvents();
            return;
        }

        events.forEach(event => {
            const card = createEventCard(event);
            eventsContainer.appendChild(card);
        });
    }

    function createEventCard(event) {
        const card = document.createElement('div');
        card.className = 'event-card';
        
        const eventDate = new Date(event.event_date || event.date);
        const formattedDate = eventDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        const formattedTime = eventDate.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        card.innerHTML = `
            <h2>${event.title}</h2>
            <div class="event-meta">
                <span>📅 ${formattedDate}</span>
                <span>🕒 ${formattedTime}</span>
            </div>
            <p>${event.description}</p>
            <div class="card-actions">
                <button class="delete-btn" onclick="deleteEvent('${event.event_id}')">Delete Event</button>
            </div>
        `;

        return card;
    }

    // Event Listeners
    searchInput.addEventListener('input', filterAndDisplayEvents);
    sortSelect.addEventListener('change', filterAndDisplayEvents);

    // Initialize
    loadEvents();
    
    // Auto-refresh every 5 minutes
    setInterval(loadEvents, 300000);

    // Make refresh function available globally
    window.refreshEvents = loadEvents;
});

// Delete event function (needs to be global for the onclick handler)
async function deleteEvent(eventId) {
    const confirmed = confirm("Are you sure you want to delete this event?");
    if (!confirmed) return;

    try {
        const res = await fetch(`${apiBaseUrl}/${eventId}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (res.ok) {
            alert("Event deleted successfully!");
            window.refreshEvents(); // Refresh the list
        } else {
            const error = await res.text();
            alert("Failed to delete event. Error: " + error);
        }
    } catch (error) {
        console.error('Error deleting event:', error);
        alert("Failed to delete event. Please try again.");
    }
}
