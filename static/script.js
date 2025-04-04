// API Endpoints
const API_BASE_URL = '/api';

// DOM Elements
const addForm = document.getElementById('addForm');
const recordsList = document.getElementById('records');
const taskTitleInput = document.getElementById('taskTitle');
const taskDescriptionInput = document.getElementById('taskDescription');
const taskStatusSelect = document.getElementById('taskStatus');

// Fetch all records
async function fetchRecords() {
    try {
        const response = await fetch(`${API_BASE_URL}/records`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        displayRecords(data);
    } catch (error) {
        console.error('Error fetching records:', error);
        showNotification('Error loading tasks', 'error');
    }
}

// Display records in the UI
function displayRecords(records) {
    if (!Array.isArray(records) || records.length === 0) {
        recordsList.innerHTML = '<p class="no-records">No tasks found. Add a new task to get started.</p>';
        return;
    }
    
    recordsList.innerHTML = '';
    records.forEach(record => {
        const recordElement = createRecordElement(record);
        recordsList.appendChild(recordElement);
    });
}

// Create HTML element for a record
// Create HTML element for a record
function createRecordElement(record) {
    const div = document.createElement('div');
    div.className = 'record-item';
    div.setAttribute('data-id', record.id);
    
    // Get status from completed field
    const status = record.completed ? 'completed' : 'pending';
    const formattedStatus = status.replace(/\b\w/g, letter => letter.toUpperCase());
    
    // Format date for display
    const formattedDate = new Date(record.created_at).toLocaleString();
    
    div.innerHTML = `
        <div class="record-info">
            <strong>${escapeHTML(record.title)}</strong>
            <p>Created: ${formattedDate}</p>
            <span class="status-badge ${status}">${formattedStatus}</span>
        </div>
        <div class="record-actions">
            <button class="edit-btn" onclick="openEditModal('${record.id}')">Edit</button>
            <button class="delete-btn" onclick="deleteRecord('${record.id}')">Delete</button>
        </div>
    `;
    return div;
}

// Helper function to escape HTML to prevent XSS
function escapeHTML(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Add new record
addForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = taskTitleInput.value.trim();
    
    if (!title) {
        showNotification('Please enter a task title', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/records`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                title,
                completed: false,
                created_at: new Date().toISOString(),
                user_id: 'abb6bcb5-436d-4a2d-90be-da08e2c6cfcb'
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        addForm.reset();
        showNotification('Task added successfully', 'success');
        fetchRecords();
    } catch (error) {
        console.error('Error adding record:', error);
        showNotification('Error adding task', 'error');
    }
});

// Open edit modal with task data
async function openEditModal(id) {
    try {
        // Find the task in the DOM to get current values
        const taskElement = document.querySelector(`.record-item[data-id="${id}"]`);
        if (!taskElement) return;
        
        const titleElement = taskElement.querySelector('strong');
        const statusElement = taskElement.querySelector('.status-badge');
        
        // Get current values
        const currentTitle = titleElement ? titleElement.textContent : '';
        const currentCompleted = statusElement && 
            statusElement.textContent.toLowerCase() === 'completed';
        
        // Use custom modal or prompt for better UX (using prompt for simplicity here)
        const title = prompt('Enter task title:', currentTitle);
        if (title === null) return; // User canceled
        
        // Simple yes/no for completed status
        const completedChoice = confirm('Mark task as completed?');
        
        if (title.trim()) {
            await updateRecord(id, title.trim(), completedChoice);
        } else {
            showNotification('Title cannot be empty', 'error');
        }
    } catch (error) {
        console.error('Error in edit flow:', error);
        showNotification('Error updating task', 'error');
    }
}

// Update record
async function updateRecord(id, title, completed) {
    try {
        const response = await fetch(`${API_BASE_URL}/records/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                title,
                completed
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        showNotification('Task updated successfully', 'success');
        fetchRecords();
    } catch (error) {
        console.error('Error updating record:', error);
        showNotification('Error updating task', 'error');
    }
}

// Delete record function can remain unchanged as it doesn't deal with the data structure
// Show notification
function showNotification(message, type = 'info') {
    // Check if notification container exists, create if not
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    notificationContainer.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 3000);
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    fetchRecords();
});