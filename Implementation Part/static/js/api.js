/**
 * API service for interacting with the attractions API
 */
class AttractionAPI {
    /**
     * Get all attractions with optional search and sorting
     * @param {string} searchTerm - Optional search term to filter attractions
     * @param {string} sortBy - Field to sort by (name, location, rating, created_at)
     * @param {string} order - Sort order (asc, desc)
     * @returns {Promise<Array>} - Promise resolving to array of attractions
     */
    static async getAttractions(searchTerm = '', sortBy = 'name', order = 'asc') {
        try {
            let url = '/api/attractions';
            const params = new URLSearchParams();
            
            if (searchTerm) {
                params.append('search', searchTerm);
            }
            
            if (sortBy) {
                params.append('sort_by', sortBy);
            }
            
            if (order) {
                params.append('order', order);
            }
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch attractions:', error);
            throw error;
        }
    }
    
    /**
     * Get a single attraction by ID
     * @param {string} id - The attraction ID
     * @returns {Promise<Object>} - Promise resolving to the attraction object
     */
    static async getAttraction(id) {
        try {
            const response = await fetch(`/api/attractions/${id}`);
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to fetch attraction ${id}:`, error);
            throw error;
        }
    }
    
    /**
     * Create a new attraction
     * @param {Object} attractionData - The attraction data to create
     * @returns {Promise<Object>} - Promise resolving to the created attraction
     */
    static async createAttraction(attractionData) {
        try {
            const response = await fetch('/api/attractions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(attractionData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to create attraction:', error);
            throw error;
        }
    }
    
    /**
     * Update an existing attraction
     * @param {string} id - The attraction ID to update
     * @param {Object} attractionData - The updated attraction data
     * @returns {Promise<Object>} - Promise resolving to the updated attraction
     */
    static async updateAttraction(id, attractionData) {
        try {
            const response = await fetch(`/api/attractions/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(attractionData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to update attraction ${id}:`, error);
            throw error;
        }
    }
    
    /**
     * Delete an attraction
     * @param {string} id - The attraction ID to delete
     * @returns {Promise<Object>} - Promise resolving to the success message
     */
    static async deleteAttraction(id) {
        try {
            const response = await fetch(`/api/attractions/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Failed to delete attraction ${id}:`, error);
            throw error;
        }
    }
}
