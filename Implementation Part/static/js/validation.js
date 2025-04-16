/**
 * Validation service for form inputs
 */
class Validator {
    /**
     * Validates the attraction form fields
     * @param {Object} formData - The form data to validate
     * @returns {Object} - Object with isValid flag and any error messages
     */
    static validateAttractionForm(formData) {
        const errors = {};
        
        // Validate name (required, min length)
        if (!formData.name || formData.name.trim() === '') {
            errors.name = 'Name is required';
        } else if (formData.name.trim().length < 2) {
            errors.name = 'Name must be at least 2 characters';
        }
        
        // Validate location (required)
        if (!formData.location || formData.location.trim() === '') {
            errors.location = 'Location is required';
        }
        
        // Validate description (required, min length)
        if (!formData.description || formData.description.trim() === '') {
            errors.description = 'Description is required';
        } else if (formData.description.trim().length < 10) {
            errors.description = 'Description must be at least 10 characters';
        }
        
        // Validate rating (required, number between 0-5)
        if (formData.rating === undefined || formData.rating === null || formData.rating === '') {
            errors.rating = 'Rating is required';
        } else {
            const rating = parseFloat(formData.rating);
            if (isNaN(rating)) {
                errors.rating = 'Rating must be a number';
            } else if (rating < 0 || rating > 5) {
                errors.rating = 'Rating must be between 0 and 5';
            }
        }
        
        // Validate image URL if provided
        if (formData.image_url && !this.isValidUrl(formData.image_url)) {
            errors.image_url = 'Please enter a valid URL';
        }
        
        // Validate website URL if provided
        if (formData.website && !this.isValidUrl(formData.website)) {
            errors.website = 'Please enter a valid URL';
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    }
    
    /**
     * Validates if a string is a valid URL
     * @param {string} url - The URL to validate
     * @returns {boolean} - True if valid URL, false otherwise
     */
    static isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
    }
    
    /**
     * Highlights form validation errors in the UI
     * @param {Object} errors - Object containing field errors
     */
    static showFormErrors(errors) {
        // Reset all form validation states
        document.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        
        // Show errors for each field
        for (const [field, message] of Object.entries(errors)) {
            const inputElement = document.getElementById(`attraction${this.capitalizeFirstLetter(field)}`);
            if (inputElement) {
                inputElement.classList.add('is-invalid');
                
                // Update feedback message
                const feedbackElement = inputElement.nextElementSibling;
                if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                    feedbackElement.textContent = message;
                }
            }
        }
    }
    
    /**
     * Helper function to capitalize the first letter of a string
     * @param {string} string - The string to capitalize
     * @returns {string} - The capitalized string
     */
    static capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
}
