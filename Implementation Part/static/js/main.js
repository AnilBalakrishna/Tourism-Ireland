// DOM Elements
const attractionsList = document.getElementById('attractionsList');
const loadingIndicator = document.getElementById('loadingIndicator');
const noAttractionsMessage = document.getElementById('noAttractionsMessage');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const sortSelect = document.getElementById('sortSelect');
const orderSelect = document.getElementById('orderSelect');
const sortBtn = document.getElementById('sortBtn');
const createNewBtn = document.getElementById('createNewBtn');
const addFirstAttractionBtn = document.getElementById('addFirstAttractionBtn');
const attractionModal = new bootstrap.Modal(document.getElementById('attractionModal'));
const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
const attractionForm = document.getElementById('attractionForm');
const modalTitle = document.getElementById('modalTitle');
const attractionId = document.getElementById('attractionId');
const attractionName = document.getElementById('attractionName');
const attractionLocation = document.getElementById('attractionLocation');
const attractionDescription = document.getElementById('attractionDescription');
const attractionRating = document.getElementById('attractionRating');
const attractionImage = document.getElementById('attractionImage');
const attractionWebsite = document.getElementById('attractionWebsite');
const saveAttractionBtn = document.getElementById('saveAttractionBtn');
const deleteAttractionName = document.getElementById('deleteAttractionName');
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
const alertToast = new bootstrap.Toast(document.getElementById('alertToast'));
const toastTitle = document.getElementById('toastTitle');
const toastMessage = document.getElementById('toastMessage');

// Current state 
let currentSearchTerm = '';
let currentSortBy = 'name';
let currentOrder = 'asc';
let currentDeleteId = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    loadAttractions();
    
    // Event Listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keyup', e => {
        if (e.key === 'Enter') handleSearch();
    });
    
    sortBtn.addEventListener('click', handleSort);
    
    createNewBtn.addEventListener('click', () => {
        resetForm();
        modalTitle.textContent = 'Add New Attraction';
        attractionModal.show();
    });
    
    addFirstAttractionBtn.addEventListener('click', () => {
        resetForm();
        modalTitle.textContent = 'Add New Attraction';
        attractionModal.show();
    });
    
    saveAttractionBtn.addEventListener('click', saveAttraction);
    
    confirmDeleteBtn.addEventListener('click', deleteAttraction);
});

/**
 * Loads attractions from the API with current search and sort parameters
 */
async function loadAttractions() {
    showLoading(true);
    
    try {
        const attractions = await AttractionAPI.getAttractions(
            currentSearchTerm, 
            currentSortBy, 
            currentOrder
        );
        
        renderAttractions(attractions);
    } catch (error) {
        showToast('Error', `Failed to load attractions: ${error.message}`, true);
    } finally {
        showLoading(false);
    }
}

/**
 * Renders attractions to the DOM
 * @param {Array} attractions - Array of attraction objects to render
 */
function renderAttractions(attractions) {
    // Clear existing attractions
    while (attractionsList.firstChild) {
        if (attractionsList.firstChild.id === 'loadingIndicator' || 
            attractionsList.firstChild.id === 'noAttractionsMessage') {
            break;
        }
        attractionsList.removeChild(attractionsList.firstChild);
    }
    
    // Show no attractions message if empty
    if (attractions.length === 0) {
        noAttractionsMessage.classList.remove('d-none');
        return;
    }
    
    noAttractionsMessage.classList.add('d-none');
    
    // Render each attraction
    attractions.forEach(attraction => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4';
        
        // Format the rating as stars
        const ratingStars = generateRatingStars(attraction.rating);
        
        // Default image if none provided
        const imageUrl = attraction.image_url || 'https://via.placeholder.com/400x300?text=No+Image+Available';
        
        // Create website button if website exists
        const websiteBtn = attraction.website ? 
            `<a href="${attraction.website}" target="_blank" class="btn btn-sm btn-outline-info me-2">
                <i class="fas fa-globe"></i> Website
            </a>` : '';
        
        col.innerHTML = `
            <div class="card attraction-card">
                <div class="card-header">
                    <h5 class="mb-0">${attraction.name}</h5>
                </div>
                <div class="card-body">
                    <div class="attraction-image" style="background-image: url('${imageUrl}')"></div>
                    <p class="attraction-location">
                        <i class="fas fa-map-marker-alt"></i> ${attraction.location}
                    </p>
                    <div class="attraction-rating">
                        ${ratingStars}
                    </div>
                    <p class="card-text">${truncateText(attraction.description, 120)}</p>
                    
                    <div class="card-actions">
                        <div>
                            <button class="btn btn-sm btn-outline-primary view-btn" data-id="${attraction.id}">
                                <i class="fas fa-eye"></i> View
                            </button>
                            ${websiteBtn}
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-success edit-btn" data-id="${attraction.id}">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${attraction.id}" data-name="${attraction.name}">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        attractionsList.appendChild(col);
        
        // Add event listeners to buttons
        col.querySelector('.view-btn').addEventListener('click', () => viewAttraction(attraction.id));
        col.querySelector('.edit-btn').addEventListener('click', () => editAttraction(attraction.id));
        col.querySelector('.delete-btn').addEventListener('click', () => showDeleteConfirmation(attraction.id, attraction.name));
    });
}

/**
 * Generates HTML for star rating display
 * @param {number} rating - The rating value (0-5)
 * @returns {string} - HTML string with star icons
 */
function generateRatingStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    
    let stars = '';
    
    // Full stars
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    
    // Half star
    if (halfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    
    // Empty stars
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    
    return `${stars} <span class="ms-1">(${rating})</span>`;
}

/**
 * Truncates text to a specific length with ellipsis
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} - Truncated text
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Shows or hides the loading indicator
 * @param {boolean} show - Whether to show loading indicator
 */
function showLoading(show) {
    if (show) {
        loadingIndicator.classList.remove('d-none');
        noAttractionsMessage.classList.add('d-none');
    } else {
        loadingIndicator.classList.add('d-none');
    }
}

/**
 * Handles the search form submission
 */
function handleSearch() {
    currentSearchTerm = searchInput.value.trim();
    loadAttractions();
}

/**
 * Handles the sort form submission
 */
function handleSort() {
    currentSortBy = sortSelect.value;
    currentOrder = orderSelect.value;
    loadAttractions();
}

/**
 * Resets the attraction form
 */
function resetForm() {
    attractionId.value = '';
    attractionForm.reset();
    
    // Remove validation classes
    document.querySelectorAll('.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
}

/**
 * View a single attraction in detail
 * @param {string} id - The attraction ID to view
 */
async function viewAttraction(id) {
    try {
        const attraction = await AttractionAPI.getAttraction(id);
        
        // Fill form but disable inputs
        attractionId.value = attraction.id;
        attractionName.value = attraction.name;
        attractionLocation.value = attraction.location;
        attractionDescription.value = attraction.description;
        attractionRating.value = attraction.rating;
        attractionImage.value = attraction.image_url || '';
        attractionWebsite.value = attraction.website || '';
        
        // Set form to view mode
        modalTitle.textContent = 'View Attraction';
        
        // Disable all form fields
        const formElements = attractionForm.elements;
        for (let i = 0; i < formElements.length; i++) {
            formElements[i].disabled = true;
        }
        
        // Hide save button
        saveAttractionBtn.style.display = 'none';
        
        attractionModal.show();
        
    } catch (error) {
        showToast('Error', `Failed to load attraction: ${error.message}`, true);
    }
}

/**
 * Prepares the form for editing an attraction
 * @param {string} id - The attraction ID to edit
 */
async function editAttraction(id) {
    try {
        const attraction = await AttractionAPI.getAttraction(id);
        
        // Fill form
        attractionId.value = attraction.id;
        attractionName.value = attraction.name;
        attractionLocation.value = attraction.location;
        attractionDescription.value = attraction.description;
        attractionRating.value = attraction.rating;
        attractionImage.value = attraction.image_url || '';
        attractionWebsite.value = attraction.website || '';
        
        // Set form to edit mode
        modalTitle.textContent = 'Edit Attraction';
        
        // Enable all form fields
        const formElements = attractionForm.elements;
        for (let i = 0; i < formElements.length; i++) {
            formElements[i].disabled = false;
        }
        
        // Show save button
        saveAttractionBtn.style.display = 'block';
        
        attractionModal.show();
        
    } catch (error) {
        showToast('Error', `Failed to load attraction: ${error.message}`, true);
    }
}

/**
 * Shows the delete confirmation modal
 * @param {string} id - The attraction ID to delete
 * @param {string} name - The attraction name
 */
function showDeleteConfirmation(id, name) {
    currentDeleteId = id;
    deleteAttractionName.textContent = name;
    deleteModal.show();
}

/**
 * Saves an attraction (create or update)
 */
async function saveAttraction() {
    // Get form data
    const formData = {
        name: attractionName.value.trim(),
        location: attractionLocation.value.trim(),
        description: attractionDescription.value.trim(),
        rating: parseFloat(attractionRating.value),
        image_url: attractionImage.value.trim(),
        website: attractionWebsite.value.trim()
    };
    
    // Validate form data
    const validation = Validator.validateAttractionForm(formData);
    
    if (!validation.isValid) {
        Validator.showFormErrors(validation.errors);
        return;
    }
    
    try {
        if (attractionId.value) {
            // Update existing attraction
            await AttractionAPI.updateAttraction(attractionId.value, formData);
            showToast('Success', 'Attraction updated successfully');
        } else {
            // Create new attraction
            await AttractionAPI.createAttraction(formData);
            showToast('Success', 'Attraction created successfully');
        }
        
        // Close modal and reload attractions
        attractionModal.hide();
        loadAttractions();
        
    } catch (error) {
        showToast('Error', `Failed to save attraction: ${error.message}`, true);
    }
}

/**
 * Deletes an attraction
 */
async function deleteAttraction() {
    if (!currentDeleteId) return;
    
    try {
        await AttractionAPI.deleteAttraction(currentDeleteId);
        showToast('Success', 'Attraction deleted successfully');
        
        // Close modal and reload attractions
        deleteModal.hide();
        loadAttractions();
        
    } catch (error) {
        showToast('Error', `Failed to delete attraction: ${error.message}`, true);
    } finally {
        currentDeleteId = null;
    }
}

/**
 * Shows a toast notification
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 * @param {boolean} isError - Whether this is an error toast
 */
function showToast(title, message, isError = false) {
    const toastElement = document.getElementById('alertToast');
    
    if (isError) {
        toastElement.classList.add('error');
    } else {
        toastElement.classList.remove('error');
    }
    
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    alertToast.show();
}
