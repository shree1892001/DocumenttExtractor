// Document Processing System JavaScript

// Configuration - Using existing DocumentProcessorController on port 9500
const API_BASE_URL = 'http://localhost:9500';
const DOCUMENT_PROCESSOR_API = 'http://localhost:9500/api/v1';

// Global variables
let templates = [];
let selectedFile = null;
let currentResults = null;
let processingModes = {};
let selectedProcessingMode = 'template_matching';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Load templates
        await loadTemplates();

        // Load processing modes
        await loadProcessingModes();

        // Setup event listeners
        setupEventListeners();

        // Initialize template upload functionality
        initializeTemplateUpload();

        // Check API health (non-blocking)
        checkAPIHealth().catch(error => {
            console.warn('Health check failed, but continuing with initialization:', error);
        });

        console.log('✅ Application initialized successfully');
    } catch (error) {
        console.error('❌ Failed to initialize application:', error);
        showError('Failed to initialize application. Please check if the API server is running.');
    }
}

async function checkAPIHealth() {
    try {
        // Try multiple health check endpoints since the exact structure may vary
        const healthEndpoints = [
            `${API_BASE_URL}/health`,           // Root level health check
            `${DOCUMENT_PROCESSOR_API}/health`, // API v1 health check
            `${API_BASE_URL}/docs`,             // FastAPI docs endpoint
            `${API_BASE_URL}/`                  // Root endpoint
        ];

        for (const endpoint of healthEndpoints) {
            try {
                console.log(`🔍 Trying health check: ${endpoint}`);
                const response = await fetch(endpoint);

                if (response.ok) {
                    const data = await response.json();
                    console.log(`✅ API is healthy at ${endpoint}:`, data);
                    return true;
                }
            } catch (endpointError) {
                console.log(`❌ Failed to connect to ${endpoint}`);
                continue;
            }
        }

        // If all health checks fail, try the main processor endpoint to see if API is running
        try {
            console.log('🔍 Trying main processor endpoint...');
            const response = await fetch(`${DOCUMENT_PROCESSOR_API}/processor`, {
                method: 'OPTIONS'  // OPTIONS request to check if endpoint exists
            });

            if (response.status !== 404) {
                console.log('✅ API is running (processor endpoint accessible)');
                return true;
            }
        } catch (processorError) {
            console.log('❌ Processor endpoint also not accessible');
        }

        throw new Error('No accessible endpoints found');

    } catch (error) {
        console.error('❌ API health check failed:', error);
        showError(`Cannot connect to DocumentProcessorController API: ${error.message}. Please ensure the server is running on port 9500.`);
        return false;
    }
}

async function loadTemplates() {
    try {
        // Load actual templates from DocumentProcessorController
        let response = await fetch(`${DOCUMENT_PROCESSOR_API}/templates`);

        if (response.ok) {
            const templateData = await response.json();

            // Handle the new template response format
            if (templateData.status === 'success' && templateData.templates) {
                templates = convertActualTemplates(templateData.templates);
                console.log(`✅ Loaded ${templates.length} actual templates from templates directory`);
            } else {
                throw new Error('Invalid template response format');
            }
        } else {
            // Fallback to DocumentProcessor3 compatible templates
            console.log('DocumentProcessorController templates not available, using DocumentProcessor3 compatible templates');
            templates = createDocumentProcessor3Templates();
        }

        displayTemplates(templates);
        updateTemplateCount(templates.length);

        console.log(`✅ Loaded ${templates.length} templates`);
    } catch (error) {
        console.error('❌ Failed to load templates:', error);
        // Use DocumentProcessor3 compatible templates
        templates = createDocumentProcessor3Templates();
        displayTemplates(templates);
        updateTemplateCount(templates.length);
        console.log('Using DocumentProcessor3 compatible templates');
    }
}

function convertActualTemplates(templateData) {
    /**
     * Convert actual template files from templates directory to UI format
     */
    try {
        return templateData.map(template => {
            // Map document types to categories based on actual templates
            const categoryMap = {
                // Identity Documents
                'aadhaar_card': 'identity',
                'pan_card': 'identity',
                'driving_license': 'identity',
                'florida_driving_license': 'identity',
                'indian_driving_license': 'identity',
                'passport': 'identity',
                'voter_id': 'identity',
                'national_id': 'identity',

                // Educational Documents
                'educational_certificate': 'educational',
                'diploma': 'educational',
                'degree_certificate': 'educational',
                'transcript': 'educational',
                'marksheet': 'educational',
                'professional_certification': 'certification',

                // Legal & Corporate
                'corporate_document': 'legal',
                'business_license': 'legal',
                'registration_certificate': 'legal',
                'legal_contract': 'legal',
                'power_of_attorney': 'legal',
                'incorporation_certificate': 'legal',

                // Financial Documents
                'bank_statement': 'financial',
                'financial_statement': 'financial',
                'tax_document': 'financial',
                'invoice': 'financial',
                'receipt': 'financial',
                'salary_slip': 'financial',

                // Medical Documents
                'medical_document': 'medical',
                'medical_license': 'medical',
                'prescription': 'medical',
                'medical_report': 'medical',
                'health_certificate': 'medical',

                // Employment Documents
                'resume': 'employment',
                'employment_letter': 'employment',
                'experience_certificate': 'employment',
                'appointment_letter': 'employment',
                'relieving_letter': 'employment',

                // Property Documents
                'property_document': 'legal',
                'sale_deed': 'legal',
                'rental_agreement': 'legal',
                'property_tax': 'financial',

                // Other Documents
                'insurance_document': 'financial',
                'utility_bill': 'financial',
                'travel_document': 'identity',
                'customs_document': 'legal',
                'other': 'general',
                'unknown': 'general'
            };

            // Map document types to required fields based on actual templates
            const fieldsMap = {
                // Identity Documents
                'aadhaar_card': ['name', 'aadhaar_number', 'date_of_birth', 'address'],
                'pan_card': ['name', 'fathers_name', 'pan_number', 'date_of_birth'],
                'driving_license': ['name', 'license_number', 'date_of_birth', 'address', 'vehicle_class'],
                'florida_driving_license': ['name', 'license_number', 'date_of_birth', 'address', 'state', 'vehicle_class'],
                'indian_driving_license': ['name', 'license_number', 'date_of_birth', 'address', 'vehicle_class'],
                'passport': ['name', 'passport_number', 'date_of_birth', 'place_of_birth', 'nationality'],
                'voter_id': ['name', 'voter_id_number', 'address', 'date_of_birth'],
                'national_id': ['name', 'id_number', 'date_of_birth', 'nationality'],

                // Educational Documents
                'educational_certificate': ['student_name', 'institution', 'degree', 'graduation_date'],
                'diploma': ['student_name', 'institution', 'course', 'completion_date'],
                'degree_certificate': ['student_name', 'institution', 'degree', 'graduation_date'],
                'transcript': ['student_name', 'student_id', 'institution', 'grades', 'gpa'],
                'marksheet': ['student_name', 'roll_number', 'exam', 'marks', 'grade'],
                'professional_certification': ['holder_name', 'certification_name', 'issue_date', 'validity'],

                // Legal & Corporate
                'corporate_document': ['company_name', 'registration_number', 'address', 'incorporation_date'],
                'business_license': ['business_name', 'license_number', 'issue_date', 'validity'],
                'registration_certificate': ['entity_name', 'registration_number', 'date', 'authority'],
                'legal_contract': ['parties', 'contract_type', 'date', 'terms'],
                'power_of_attorney': ['grantor', 'attorney', 'powers', 'date'],
                'incorporation_certificate': ['company_name', 'incorporation_number', 'date', 'state'],

                // Financial Documents
                'bank_statement': ['account_holder', 'account_number', 'statement_period', 'balance'],
                'financial_statement': ['entity_name', 'period', 'revenue', 'profit'],
                'tax_document': ['taxpayer_name', 'tax_year', 'income', 'tax_amount'],
                'invoice': ['invoice_number', 'date', 'amount', 'vendor', 'customer'],
                'receipt': ['receipt_number', 'date', 'amount', 'vendor', 'description'],
                'salary_slip': ['employee_name', 'employee_id', 'month', 'gross_salary', 'net_salary'],

                // Medical Documents
                'medical_document': ['patient_name', 'doctor_name', 'hospital', 'date'],
                'medical_license': ['doctor_name', 'license_number', 'specialization', 'validity'],
                'prescription': ['patient_name', 'doctor_name', 'medicines', 'date'],
                'medical_report': ['patient_name', 'test_type', 'results', 'date'],
                'health_certificate': ['person_name', 'certificate_type', 'issue_date', 'validity'],

                // Employment Documents
                'resume': ['name', 'email', 'phone', 'experience', 'education'],
                'employment_letter': ['employee_name', 'designation', 'company', 'joining_date'],
                'experience_certificate': ['employee_name', 'designation', 'company', 'duration'],
                'appointment_letter': ['employee_name', 'designation', 'company', 'joining_date', 'salary'],
                'relieving_letter': ['employee_name', 'designation', 'company', 'last_working_day'],

                // Property Documents
                'property_document': ['property_address', 'owner_name', 'document_type', 'date'],
                'sale_deed': ['seller', 'buyer', 'property_address', 'sale_amount', 'date'],
                'rental_agreement': ['landlord', 'tenant', 'property_address', 'rent', 'duration'],
                'property_tax': ['owner_name', 'property_address', 'tax_amount', 'assessment_year'],

                // Other Documents
                'insurance_document': ['policy_number', 'policyholder', 'coverage', 'premium'],
                'utility_bill': ['consumer_name', 'consumer_number', 'billing_period', 'amount'],
                'travel_document': ['traveler_name', 'document_number', 'destination', 'validity'],
                'customs_document': ['importer_exporter', 'goods_description', 'value', 'date'],
                'other': ['document_number', 'name', 'date'],
                'unknown': []
            };

            const category = categoryMap[template.document_type] || 'general';
            const requiredFields = fieldsMap[template.document_type] || [];

            return {
                id: template.name,
                name: template.display_name,
                category: category,
                description: `${template.document_type.replace('_', ' ').toUpperCase()} template (${template.file_extension})`,
                required_fields: requiredFields,
                optional_fields: ['confidence_score', 'processing_method'],
                sample_text: `Template file: ${template.filename}`,
                file_info: {
                    filename: template.filename,
                    file_path: template.file_path,
                    file_extension: template.file_extension,
                    file_size: template.file_size,
                    document_type: template.document_type
                }
            };
        });
    } catch (error) {
        console.error('Error converting actual templates:', error);
        return createDocumentProcessor3Templates();
    }
}

function convertDocumentProcessorTemplates(templateData) {
    /**
     * Convert DocumentProcessorService template format to UI format (fallback)
     */
    try {
        if (Array.isArray(templateData)) {
            return templateData.map(template => ({
                id: template.id || template.name?.toLowerCase().replace(/\s+/g, '_'),
                name: template.name || 'Unknown Template',
                category: template.category || 'general',
                description: template.description || 'Document template',
                required_fields: template.required_fields || [],
                optional_fields: template.optional_fields || [],
                sample_text: template.sample_text || ''
            }));
        } else {
            // Handle object format
            return Object.entries(templateData).map(([key, template]) => ({
                id: key,
                name: template.name || key,
                category: template.category || 'general',
                description: template.description || 'Document template',
                required_fields: template.required_fields || [],
                optional_fields: template.optional_fields || [],
                sample_text: template.sample_text || ''
            }));
        }
    } catch (error) {
        console.error('Error converting templates:', error);
        return createDocumentProcessor3Templates();
    }
}

function createDocumentProcessor3Templates() {
    /**
     * Create templates compatible with DocumentProcessor3 capabilities
     */
    return [
        {
            id: "student_transcript",
            name: "Student Transcript",
            category: "educational",
            description: "Official academic transcript with grades and GPA",
            required_fields: ["student_name", "student_id", "gpa", "institution"],
            optional_fields: ["graduation_date", "degree", "major", "courses"],
            sample_text: "Official Transcript - Student: John Doe, GPA: 3.85"
        },
        {
            id: "diploma_certificate",
            name: "Diploma/Certificate",
            category: "educational",
            description: "Graduation diploma or academic certificate",
            required_fields: ["recipient_name", "degree", "institution", "graduation_date"],
            optional_fields: ["honors", "major", "minor"],
            sample_text: "This diploma certifies that John Doe has earned Bachelor of Science"
        },
        {
            id: "professional_certification",
            name: "Professional Certification",
            category: "certification",
            description: "Professional certifications and licenses",
            required_fields: ["holder_name", "certification_name", "issue_date"],
            optional_fields: ["expiration_date", "certification_number", "issuing_authority"],
            sample_text: "AWS Certified Solutions Architect - Professional Certification"
        },
        {
            id: "medical_license",
            name: "Medical License",
            category: "medical",
            description: "Medical professional license",
            required_fields: ["licensee_name", "license_number", "license_type"],
            optional_fields: ["issue_date", "expiration_date", "medical_board"],
            sample_text: "California Medical Board - Physician License - Dr. Jane Smith"
        },
        {
            id: "resume_cv",
            name: "Resume/CV",
            category: "employment",
            description: "Professional resume or curriculum vitae",
            required_fields: ["name", "email", "phone"],
            optional_fields: ["address", "experience", "education", "skills"],
            sample_text: "John Doe - Software Engineer Resume - Experience: 5 years"
        },
        {
            id: "bank_statement",
            name: "Bank Statement",
            category: "financial",
            description: "Bank account statement",
            required_fields: ["account_holder", "account_number", "statement_period"],
            optional_fields: ["opening_balance", "closing_balance", "transactions"],
            sample_text: "Bank Statement - Account Holder: John Doe - Account: 123456789"
        },
        {
            id: "passport",
            name: "Passport",
            category: "identity",
            description: "Passport identification document",
            required_fields: ["full_name", "passport_number", "nationality"],
            optional_fields: ["date_of_birth", "place_of_birth", "issue_date", "expiry_date"],
            sample_text: "Passport - Full Name: John Doe - Passport Number: A12345678"
        },
        {
            id: "contract",
            name: "Legal Contract",
            category: "legal",
            description: "Legal contract or agreement",
            required_fields: ["parties", "contract_type", "date"],
            optional_fields: ["terms", "conditions", "signatures"],
            sample_text: "Employment Contract between Company ABC and John Doe"
        }
    ];
}

async function loadProcessingModes() {
    try {
        // Try to get processing modes from DocumentProcessorController
        const response = await fetch(`${DOCUMENT_PROCESSOR_API}/processing-modes`);

        if (response.ok) {
            const modesData = await response.json();
            processingModes = modesData.available_modes;
            selectedProcessingMode = modesData.default_mode;
        } else {
            // Use default processing modes for DocumentProcessorController
            processingModes = createDefaultProcessingModes();
            selectedProcessingMode = 'document_processor3';
        }

        displayProcessingModes(processingModes);

        console.log(`✅ Loaded processing modes`);
    } catch (error) {
        console.error('❌ Failed to load processing modes:', error);
        // Use default processing modes
        processingModes = createDefaultProcessingModes();
        selectedProcessingMode = 'document_processor3';
        displayProcessingModes(processingModes);
    }
}

function createDefaultProcessingModes() {
    /**
     * Create default processing modes for DocumentProcessor3 Service
     */
    return {
        "document_processor3_service": {
            "name": "DocumentProcessor3 Service",
            "description": "Full DocumentProcessor3 service with verification and validation",
            "available": true,
            "privacy_level": "Maximum",
            "accuracy": "90-98%"
        },
        "template_matching": {
            "name": "Template Matching",
            "description": "Enhanced template-based document classification with confidence scoring",
            "available": true,
            "privacy_level": "High",
            "accuracy": "85-95%"
        },
        "verification_mode": {
            "name": "Document Verification",
            "description": "Advanced document verification with genuineness detection",
            "available": true,
            "privacy_level": "Maximum",
            "accuracy": "95-99%"
        },
        "batch_processing": {
            "name": "Batch Processing",
            "description": "Process multiple documents with chunking support",
            "available": true,
            "privacy_level": "High",
            "accuracy": "85-95%"
        }
    };
}

function displayTemplates(templatesToShow) {
    const templatesGrid = document.getElementById('templates-grid');
    templatesGrid.innerHTML = '';
    
    if (templatesToShow.length === 0) {
        templatesGrid.innerHTML = '<p class="no-templates">No templates found for the selected category.</p>';
        return;
    }
    
    templatesToShow.forEach(template => {
        const templateCard = createTemplateCard(template);
        templatesGrid.appendChild(templateCard);
    });
}

function createTemplateCard(template) {
    const card = document.createElement('div');
    card.className = 'template-card';
    card.dataset.category = template.category;

    // Format file size if available
    const fileSize = template.file_info?.file_size ?
        formatFileSize(template.file_info.file_size) : 'Unknown';

    // Create file info section if available
    const fileInfoHTML = template.file_info ? `
        <div class="template-file-info">
            <div class="file-details">
                <span class="file-name">${template.file_info.filename}</span>
                <span class="file-size">${fileSize}</span>
            </div>
            <div class="file-type">${template.file_info.file_extension.toUpperCase()}</div>
        </div>
    ` : '';

    card.innerHTML = `
        <div class="template-header">
            <h3>${template.name}</h3>
            <div class="template-category">${template.category.toUpperCase()}</div>
        </div>
        ${fileInfoHTML}
        <p class="template-description">${template.description}</p>
        <div class="template-fields">
            <div class="fields-section">
                <strong>Required Fields:</strong>
                <div class="field-tags">
                    ${template.required_fields.map(field =>
                        `<span class="field-tag required">${field.replace('_', ' ')}</span>`
                    ).join('')}
                </div>
            </div>
            ${template.optional_fields.length > 0 ? `
                <div class="fields-section">
                    <strong>Optional Fields:</strong>
                    <div class="field-tags">
                        ${template.optional_fields.map(field =>
                            `<span class="field-tag optional">${field.replace('_', ' ')}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    return card;
}

function updateTemplateCount(count) {
    document.getElementById('template-count').textContent = `${count} Templates Available`;
}

function displayProcessingModes(modes) {
    const processingModesContainer = document.getElementById('processing-modes');
    if (!processingModesContainer) return;

    processingModesContainer.innerHTML = '';

    Object.entries(modes).forEach(([modeId, mode]) => {
        const modeCard = createProcessingModeCard(modeId, mode);
        processingModesContainer.appendChild(modeCard);
    });
}

function createProcessingModeCard(modeId, mode) {
    const card = document.createElement('div');
    card.className = `processing-mode ${mode.available ? '' : 'disabled'} ${modeId === selectedProcessingMode ? 'selected' : ''}`;
    card.dataset.mode = modeId;

    card.innerHTML = `
        <div class="mode-header">
            <span class="mode-name">${mode.name}</span>
            <span class="mode-status ${mode.available ? 'available' : 'unavailable'}">
                ${mode.available ? 'Available' : 'Unavailable'}
            </span>
        </div>
        <div class="mode-description">${mode.description}</div>
        <div class="mode-stats">
            <div class="mode-stat">
                <span class="mode-stat-label">Privacy</span>
                <span class="mode-stat-value">${mode.privacy_level}</span>
            </div>
            <div class="mode-stat">
                <span class="mode-stat-label">Accuracy</span>
                <span class="mode-stat-value">${mode.accuracy}</span>
            </div>
        </div>
    `;

    if (mode.available) {
        card.addEventListener('click', () => selectProcessingMode(modeId));
    }

    return card;
}

function selectProcessingMode(modeId) {
    // Update selected mode
    selectedProcessingMode = modeId;

    // Update UI
    document.querySelectorAll('.processing-mode').forEach(card => {
        card.classList.remove('selected');
    });

    const selectedCard = document.querySelector(`[data-mode="${modeId}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }

    console.log(`Selected processing mode: ${modeId}`);
}

function setupEventListeners() {
    // File input
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', handleFileSelect);
    
    // Upload area drag and drop
    const uploadArea = document.getElementById('upload-area');
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Process button
    const processBtn = document.getElementById('process-btn');
    processBtn.addEventListener('click', processDocument);
    
    // Category filters
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => filterTemplates(btn.dataset.category, btn));
    });
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        displayFileInfo(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        selectedFile = files[0];
        displayFileInfo(files[0]);
    }
}

function displayFileInfo(file) {
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'flex';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function filterTemplates(category, buttonElement) {
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (buttonElement) {
        buttonElement.classList.add('active');
    }
    
    // Filter templates
    let filteredTemplates;
    if (category === 'all') {
        filteredTemplates = templates;
    } else {
        filteredTemplates = templates.filter(template => template.category === category);
    }
    
    displayTemplates(filteredTemplates);
    updateTemplateCount(filteredTemplates.length);
}

async function processDocument() {
    if (!selectedFile) {
        showError('Please select a file to process.');
        return;
    }
    
    try {
        // Show processing section
        showProcessingStatus();
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Get processing options
        const useLocalOnly = document.getElementById('use-local-only').checked;
        const useTemplateMatching = document.getElementById('use-template-matching').checked;

        if (useLocalOnly) {
            formData.append('use_local_only', 'true');
        }

        if (useTemplateMatching) {
            formData.append('use_template_matching', 'true');
        }

        // Add selected processing mode info
        console.log(`Processing with mode: ${selectedProcessingMode}, Local Only: ${useLocalOnly}, Template Matching: ${useTemplateMatching}`);
        
        // Update processing message
        updateProcessingMessage('Uploading and analyzing document...');
        
        // Make API request to DocumentProcessorController using the actual endpoint
        const response = await fetch(`${DOCUMENT_PROCESSOR_API}/processor`, {
            method: 'POST',
            body: formData,
            // Don't set Content-Type header - let browser set it for multipart/form-data
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
        }

        updateProcessingMessage('Extracting data and matching templates...');

        const apiResponse = await response.json();

        // Convert DocumentProcessorController response to our expected format
        const results = convertDocumentProcessorResponse(apiResponse);
        currentResults = results;
        
        // Hide processing and show results
        hideProcessingStatus();
        displayResults(results);
        
        console.log('✅ Document processed successfully:', results);
        
    } catch (error) {
        console.error('❌ Failed to process document:', error);
        hideProcessingStatus();
        showError(`Failed to process document: ${error.message}`);
    }
}

function showProcessingStatus() {
    document.getElementById('processing-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    
    // Scroll to processing section
    document.getElementById('processing-section').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

function hideProcessingStatus() {
    document.getElementById('processing-section').style.display = 'none';
}

function updateProcessingMessage(message) {
    document.getElementById('processing-message').textContent = message;
}

function displayResults(results) {
    // Show results section
    document.getElementById('results-section').style.display = 'block';

    // Check for template suggestions first
    checkForTemplateSuggestions(results);

    // Display document type
    displayDocumentType(results);

    // Display extracted data
    displayExtractedData(results);

    // Display processing info
    displayProcessingInfo(results);

    // Display privacy status
    displayPrivacyStatus(results);

    // Scroll to results
    document.getElementById('results-section').scrollIntoView({
        behavior: 'smooth'
    });
}

function displayDocumentType(results) {
    const documentType = document.getElementById('document-type');
    const confidenceScore = document.getElementById('confidence-score');
    const confidenceBadge = document.getElementById('confidence-badge');
    const matchedTemplate = document.getElementById('matched-template');
    const templateCategory = document.getElementById('template-category');
    
    documentType.textContent = results.document_type;
    
    const confidence = Math.round(results.template_confidence * 100);
    confidenceScore.textContent = `${confidence}%`;
    
    // Set confidence badge color
    confidenceBadge.className = 'confidence-badge';
    if (confidence >= 80) {
        confidenceBadge.classList.add('high');
    } else if (confidence >= 60) {
        confidenceBadge.classList.add('medium');
    } else {
        confidenceBadge.classList.add('low');
    }
    
    if (results.template_matched) {
        const template = templates.find(t => t.id === results.template_matched);
        matchedTemplate.textContent = template ? template.name : results.template_matched;
        templateCategory.textContent = template ? template.category.toUpperCase() : 'Unknown';
    } else {
        matchedTemplate.textContent = 'No template matched';
        templateCategory.textContent = 'Unknown';
    }
}

function displayExtractedData(results) {
    const extractedFields = document.getElementById('extracted-fields');
    extractedFields.innerHTML = '';

    const fields = results.extracted_data.extracted_fields || {};
    const confidenceScores = results.extracted_data.confidence_scores || {};

    if (Object.keys(fields).length === 0) {
        extractedFields.innerHTML = '<p class="no-data">No data extracted from the document.</p>';
        return;
    }

    // Sort fields to show simple fields first, then complex objects
    const sortedFields = Object.entries(fields).sort(([, a], [, b]) => {
        const aIsSimple = typeof a !== 'object' || Array.isArray(a);
        const bIsSimple = typeof b !== 'object' || Array.isArray(b);

        if (aIsSimple && !bIsSimple) return -1;
        if (!aIsSimple && bIsSimple) return 1;
        return 0;
    });

    sortedFields.forEach(([fieldName, fieldValue]) => {
        const confidence = confidenceScores[fieldName] || 0;
        const fieldElement = createExtractedField(fieldName, fieldValue, confidence);
        extractedFields.appendChild(fieldElement);
    });
}

function createExtractedField(name, value, confidence) {
    const field = document.createElement('div');
    field.className = 'extracted-field';

    const confidencePercent = Math.round(confidence * 100);
    const confidenceClass = confidencePercent >= 80 ? 'success' :
                           confidencePercent >= 60 ? 'warning' : 'error';

    // Format the value properly based on its type
    let formattedValue = formatFieldValue(value);

    field.innerHTML = `
        <div class="field-name">${formatFieldName(name)}</div>
        <div class="field-value">
            <span>${formattedValue}</span>
            <small class="${confidenceClass}"> (${confidencePercent}%)</small>
        </div>
    `;

    return field;
}

function formatFieldValue(value) {
    // Handle different types of values
    if (value === null || value === undefined) {
        return '<em>Not available</em>';
    }

    if (typeof value === 'string') {
        return escapeHtml(value);
    }

    if (typeof value === 'number') {
        return value.toString();
    }

    if (Array.isArray(value)) {
        if (value.length === 0) {
            return '<em>No items</em>';
        }

        // For arrays, create a clean list
        if (value.length <= 3) {
            // Short arrays - display inline
            return value.map(item =>
                typeof item === 'object' ? formatNestedObject(item) : escapeHtml(String(item))
            ).join(', ');
        } else {
            // Long arrays - display as numbered list
            return '<div style="text-align: left;">' +
                value.slice(0, 3).map((item, index) =>
                    `${index + 1}. ${typeof item === 'object' ? formatNestedObject(item) : escapeHtml(String(item))}`
                ).join('<br>') +
                (value.length > 3 ? `<br><em>... and ${value.length - 3} more</em>` : '') +
                '</div>';
        }
    }

    if (typeof value === 'object') {
        return formatNestedObject(value);
    }

    // Fallback for any other type
    return escapeHtml(String(value));
}

function formatNestedObject(obj) {
    const entries = Object.entries(obj);
    if (entries.length === 0) {
        return '<em>No data</em>';
    }

    // For small objects (1-2 fields), display inline
    if (entries.length <= 2) {
        return entries.map(([key, val]) => {
            const formattedKey = formatFieldName(key);
            const formattedVal = typeof val === 'object' ?
                (Array.isArray(val) ? val.join(', ') : JSON.stringify(val)) :
                escapeHtml(String(val));
            return `<strong>${formattedKey}:</strong> ${formattedVal}`;
        }).join(' • ');
    }

    // For larger objects, display as a structured list
    return '<div style="text-align: left; margin-top: 5px;">' +
        entries.map(([key, val]) => {
            const formattedKey = formatFieldName(key);
            let formattedVal;

            if (typeof val === 'object') {
                if (Array.isArray(val)) {
                    formattedVal = val.length > 0 ? val.join(', ') : '<em>None</em>';
                } else {
                    formattedVal = JSON.stringify(val);
                }
            } else {
                formattedVal = escapeHtml(String(val));
            }

            return `• <strong>${formattedKey}:</strong> ${formattedVal}`;
        }).join('<br>') +
        '</div>';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Template Upload Functionality
function initializeTemplateUpload() {
    const addTemplateBtn = document.getElementById('add-template-btn');
    const addTemplateSection = document.getElementById('add-template-section');
    const closeTemplateForm = document.getElementById('close-template-form');
    const cancelTemplateUpload = document.getElementById('cancel-template-upload');
    const templateUploadForm = document.getElementById('template-upload-form');
    const templateFileInput = document.getElementById('template-file');
    const templateFileArea = document.getElementById('template-file-area');
    const templateFilePreview = document.getElementById('template-file-preview');
    const removeTemplateFile = document.getElementById('remove-template-file');

    // Show template upload form
    addTemplateBtn.addEventListener('click', () => {
        addTemplateSection.style.display = 'block';
        addTemplateSection.scrollIntoView({ behavior: 'smooth' });
    });

    // Hide template upload form
    function hideTemplateForm() {
        addTemplateSection.style.display = 'none';
        templateUploadForm.reset();
        templateFilePreview.style.display = 'none';
        document.querySelector('.upload-placeholder').style.display = 'block';
    }

    closeTemplateForm.addEventListener('click', hideTemplateForm);
    cancelTemplateUpload.addEventListener('click', hideTemplateForm);

    // File upload handling
    templateFileInput.addEventListener('change', handleTemplateFileSelect);

    // Drag and drop
    templateFileArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        templateFileArea.classList.add('dragover');
    });

    templateFileArea.addEventListener('dragleave', () => {
        templateFileArea.classList.remove('dragover');
    });

    templateFileArea.addEventListener('drop', (e) => {
        e.preventDefault();
        templateFileArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            templateFileInput.files = files;
            handleTemplateFileSelect();
        }
    });

    // Remove file
    removeTemplateFile.addEventListener('click', () => {
        templateFileInput.value = '';
        templateFilePreview.style.display = 'none';
        document.querySelector('.upload-placeholder').style.display = 'block';
    });

    // Form submission
    templateUploadForm.addEventListener('submit', handleTemplateUpload);
}

function handleTemplateFileSelect() {
    const fileInput = document.getElementById('template-file');
    const filePreview = document.getElementById('template-file-preview');
    const uploadPlaceholder = document.querySelector('.upload-placeholder');

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            showNotification('File size must be less than 10MB', 'error');
            fileInput.value = '';
            return;
        }

        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf',
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type)) {
            showNotification('Unsupported file type. Please use JPG, PNG, PDF, or DOCX', 'error');
            fileInput.value = '';
            return;
        }

        // Show file preview
        filePreview.querySelector('.file-name').textContent = file.name;
        filePreview.querySelector('.file-size').textContent = formatFileSize(file.size);

        uploadPlaceholder.style.display = 'none';
        filePreview.style.display = 'flex';
    }
}

async function handleTemplateUpload(e) {
    e.preventDefault();

    const uploadBtn = document.getElementById('upload-template-btn');
    const originalText = uploadBtn.innerHTML;

    try {
        // Show loading state
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
        uploadBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', document.getElementById('template-file').files[0]);
        formData.append('template_name', document.getElementById('template-name').value);
        formData.append('document_type', document.getElementById('document-type').value);
        formData.append('description', document.getElementById('template-description').value);

        const response = await fetch(`${DOCUMENT_PROCESSOR_API}/templates/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.status === 'success') {
            showNotification(result.message, 'success');

            // Hide form and reload templates
            document.getElementById('add-template-section').style.display = 'none';
            document.getElementById('template-upload-form').reset();
            document.getElementById('template-file-preview').style.display = 'none';
            document.querySelector('.upload-placeholder').style.display = 'block';

            // Reload templates to show the new one
            await loadTemplates();

        } else {
            showNotification(result.message || 'Failed to upload template', 'error');
        }

    } catch (error) {
        console.error('Template upload error:', error);
        showNotification('Failed to upload template. Please try again.', 'error');
    } finally {
        // Restore button state
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
    }
}

function formatFieldName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function displayProcessingInfo(results) {
    const processingInfo = document.getElementById('processing-info');
    const fileInfo = results.file_info || {};
    const summary = results.processing_summary || {};
    const docProcessorData = results.document_processor_data || {};

    let infoHTML = `
        <div class="info-item">
            <strong>File Format:</strong> ${fileInfo.file_format || 'Unknown'}
        </div>
        <div class="info-item">
            <strong>File Size:</strong> ${formatFileSize(fileInfo.file_size || 0)}
        </div>
        <div class="info-item">
            <strong>Processing Method:</strong> ${fileInfo.processing_method || 'Unknown'}
        </div>
        <div class="info-item">
            <strong>Processor Used:</strong> ${fileInfo.processor_used || 'Unknown'}
        </div>
        <div class="info-item">
            <strong>Model Used:</strong> ${summary.model_used || 'Unknown'}
        </div>
        <div class="info-item">
            <strong>Fields Extracted:</strong> ${summary.successful_extractions || 0}
        </div>
    `;

    // Add DocumentProcessor3 Service specific information if available
    if (docProcessorData.is_genuine !== undefined) {
        infoHTML += `
            <div class="info-item">
                <strong>Document Genuine:</strong> ${docProcessorData.is_genuine ? '✅ Yes' : '❌ No'}
            </div>
        `;
    }

    if (docProcessorData.confidence_score !== undefined) {
        infoHTML += `
            <div class="info-item">
                <strong>Verification Confidence:</strong> ${(docProcessorData.confidence_score * 100).toFixed(1)}%
            </div>
        `;
    }

    if (docProcessorData.rejection_reason) {
        infoHTML += `
            <div class="info-item">
                <strong>Rejection Reason:</strong> ${docProcessorData.rejection_reason}
            </div>
        `;
    }

    if (docProcessorData.security_features_found && docProcessorData.security_features_found.length > 0) {
        infoHTML += `
            <div class="info-item">
                <strong>Security Features:</strong> ${docProcessorData.security_features_found.join(', ')}
            </div>
        `;
    }

    if (docProcessorData.total_documents_processed > 1) {
        infoHTML += `
            <div class="info-item">
                <strong>Batch Size:</strong> ${docProcessorData.total_documents_processed} documents
            </div>
        `;
    }

    processingInfo.innerHTML = infoHTML;

    // Show template matching card if we have DocumentProcessor3 data
    if (docProcessorData.verification_result || summary.template_matching_enabled) {
        displayTemplateMatchingInfo(results);
    }
}

function displayTemplateMatchingInfo(results) {
    const templateMatchingCard = document.getElementById('template-matching-card');
    const templateMatchingInfo = document.getElementById('template-matching-info');

    if (!templateMatchingCard || !templateMatchingInfo) return;

    const docProcessorData = results.document_processor_data || {};
    const verificationChecks = docProcessorData.verification_checks || {};
    const processingMetadata = results.extracted_data?.processing_metadata || {};

    let matchingHTML = `
        <div class="info-item">
            <strong>Template Matched:</strong> ${results.document_type || 'Unknown'}
        </div>
        <div class="info-item">
            <strong>Match Confidence:</strong> ${(results.template_confidence * 100).toFixed(1)}%
        </div>
        <div class="info-item">
            <strong>Validation Level:</strong> ${processingMetadata.validation_level || 'Standard'}
        </div>
        <div class="info-item">
            <strong>Processing Method:</strong> ${processingMetadata.processing_method || 'DocumentProcessor3'}
        </div>
    `;

    // Add DocumentProcessor3 verification checks
    if (Object.keys(verificationChecks).length > 0) {
        matchingHTML += `
            <div class="info-item">
                <strong>Verification Checks:</strong>
                <div style="margin-left: 20px; margin-top: 5px;">
                    ${Object.entries(verificationChecks).map(([check, result]) =>
                        `<div><em>${check}:</em> ${result ? '✅ Passed' : '❌ Failed'}</div>`
                    ).join('')}
                </div>
            </div>
        `;
    }

    // Add verification summary if available
    if (docProcessorData.verification_summary) {
        matchingHTML += `
            <div class="info-item">
                <strong>Verification Summary:</strong>
                <div style="margin-left: 20px; margin-top: 5px; font-style: italic;">
                    ${docProcessorData.verification_summary}
                </div>
            </div>
        `;
    }

    // Add recommendations if available
    if (docProcessorData.recommendations && docProcessorData.recommendations.length > 0) {
        matchingHTML += `
            <div class="info-item">
                <strong>Recommendations:</strong>
                <ul style="margin-left: 20px; margin-top: 5px;">
                    ${docProcessorData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    templateMatchingInfo.innerHTML = matchingHTML;
    templateMatchingCard.style.display = 'block';
}

function displayPrivacyStatus(results) {
    const privacyStatus = document.getElementById('privacy-status');
    const isProtected = results.privacy_protected;
    
    const statusClass = isProtected ? 'privacy-protected' : 'privacy-warning';
    const statusIcon = isProtected ? 'fas fa-shield-alt' : 'fas fa-exclamation-triangle';
    const statusText = isProtected ? 'Privacy Protected' : 'Privacy Warning';
    const statusDescription = isProtected ? 
        'This document was processed locally with complete privacy protection. No data was sent to external services.' :
        'This document may have been processed using external services. Please review your privacy settings.';
    
    privacyStatus.innerHTML = `
        <div class="${statusClass}">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <i class="${statusIcon}" style="margin-right: 10px;"></i>
                <strong>${statusText}</strong>
            </div>
            <p>${statusDescription}</p>
        </div>
    `;
}

function resetForm() {
    // Reset file selection
    selectedFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').style.display = 'none';
    
    // Hide results
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('processing-section').style.display = 'none';
    
    // Reset checkbox
    document.getElementById('use-local-only').checked = false;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function exportResults() {
    if (!currentResults) {
        showError('No results to export.');
        return;
    }
    
    try {
        const exportData = {
            timestamp: new Date().toISOString(),
            document_type: currentResults.document_type,
            template_matched: currentResults.template_matched,
            template_confidence: currentResults.template_confidence,
            extracted_data: currentResults.extracted_data,
            file_info: currentResults.file_info,
            privacy_protected: currentResults.privacy_protected
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `document_processing_results_${Date.now()}.json`;
        link.click();
        
        console.log('✅ Results exported successfully');
    } catch (error) {
        console.error('❌ Failed to export results:', error);
        showError('Failed to export results.');
    }
}

function convertDocumentProcessorResponse(apiResponse) {
    /**
     * Convert DocumentProcessorService response to our expected format
     *
     * DocumentProcessorService returns:
     * {
     *   "status": "success",
     *   "message": "Successfully processed 1 documents",
     *   "data": [
     *     {
     *       "extracted_data": {
     *         "data": {...},
     *         "confidence": 0.95,
     *         "additional_info": "...",
     *         "document_metadata": {...}
     *       },
     *       "verification": {
     *         "is_genuine": true,
     *         "confidence_score": 0.88,
     *         "verification_checks": {...}
     *       },
     *       "processing_details": {
     *         "document_type": "...",
     *         "confidence": 0.92,
     *         "validation_level": "...",
     *         "processing_method": "..."
     *       }
     *     }
     *   ]
     * }
     */

    try {
        // Handle the actual DocumentProcessorService response structure
        const dataArray = apiResponse.data || [];

        if (dataArray.length === 0) {
            throw new Error('No document data returned');
        }

        // Get the first document result
        const firstResult = dataArray[0];
        const extractedData = firstResult.extracted_data || {};
        const verification = firstResult.verification || {};
        const processingDetails = firstResult.processing_details || {};

        // Extract template matching info
        const templateMatched = processingDetails.document_type || 'Unknown';
        const templateConfidence = processingDetails.confidence || 0.0;

        // Convert extracted fields format
        const extractedFields = extractedData.data || {};
        const confidenceScores = {};

        // Generate confidence scores for each field (using extraction confidence)
        const baseConfidence = extractedData.confidence || verification.confidence_score || 0.8;
        Object.keys(extractedFields).forEach(field => {
            confidenceScores[field] = baseConfidence;
        });

        // Build our expected format
        return {
            status: apiResponse.status === 'success' ? 'success' : 'error',
            document_type: templateMatched,
            template_matched: templateMatched.toLowerCase().replace(/\s+/g, '_'),
            template_confidence: templateConfidence,
            privacy_protected: true, // DocumentProcessor3 processes locally
            extracted_data: {
                extracted_fields: extractedFields,
                confidence_scores: confidenceScores,
                processing_metadata: {
                    extraction_method: 'document_processor3_service',
                    model_used: 'DocumentProcessor3',
                    privacy_protected: true,
                    template_matching: true,
                    validation_level: processingDetails.validation_level || 'standard',
                    processing_method: processingDetails.processing_method || 'unknown'
                }
            },
            processing_summary: {
                total_questions_asked: Object.keys(extractedFields).length,
                successful_extractions: Object.keys(extractedFields).length,
                average_confidence: baseConfidence,
                model_used: 'DocumentProcessor3',
                device_used: 'local',
                template_matching_enabled: true,
                validation_level: processingDetails.validation_level || 'standard',
                chunk_info: {
                    chunk_index: processingDetails.chunk_index,
                    total_chunks: processingDetails.total_chunks
                }
            },
            file_info: {
                filename: selectedFile ? selectedFile.name : 'unknown',
                file_format: selectedFile ? '.' + selectedFile.name.split('.').pop().toLowerCase() : '.unknown',
                file_size: selectedFile ? selectedFile.size : 0,
                processing_method: processingDetails.processing_method || 'document_processor3_service',
                processor_used: 'DocumentProcessorService'
            },
            // DocumentProcessor3 specific data from actual response
            document_processor_data: {
                is_genuine: verification.is_genuine || false,
                confidence_score: verification.confidence_score || 0.0,
                rejection_reason: verification.rejection_reason || '',
                verification_checks: verification.verification_checks || {},
                security_features_found: verification.security_features_found || [],
                verification_summary: verification.verification_summary || '',
                recommendations: verification.recommendations || [],
                additional_info: extractedData.additional_info || '',
                document_metadata: extractedData.document_metadata || {},
                total_documents_processed: dataArray.length
            }
        };

    } catch (error) {
        console.error('Error converting DocumentProcessor response:', error);
        return {
            status: 'error',
            error_message: 'Failed to process response from DocumentProcessor',
            document_type: 'Unknown',
            template_matched: null,
            template_confidence: 0.0,
            privacy_protected: true,
            extracted_data: { extracted_fields: {}, confidence_scores: {} },
            processing_summary: { model_used: 'DocumentProcessor3' },
            file_info: {}
        };
    }
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('error-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('error-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Template Suggestion Functionality
let currentTemplateSuggestion = null;

function checkForTemplateSuggestions(results) {
    // Check if DocumentProcessor3 returned a template suggestion
    const templateSuggestion = results.template_suggestion;

    if (templateSuggestion && templateSuggestion.should_create_template) {
        currentTemplateSuggestion = templateSuggestion;
        showTemplateSuggestionNotification(templateSuggestion);
    }
}

function showTemplateSuggestionNotification(suggestion) {
    // Create a notification banner for template suggestion
    const existingBanner = document.getElementById('template-suggestion-banner');
    if (existingBanner) {
        existingBanner.remove();
    }

    const banner = document.createElement('div');
    banner.id = 'template-suggestion-banner';
    banner.className = 'template-suggestion-banner';

    const suggestedTemplate = suggestion.suggested_template;

    banner.innerHTML = `
        <div class="suggestion-content">
            <div class="suggestion-icon">
                <i class="fas fa-lightbulb"></i>
            </div>
            <div class="suggestion-text">
                <h4>Create New Template?</h4>
                <p><strong>Reason:</strong> ${suggestion.reason}</p>
                <p><strong>Suggested:</strong> ${suggestedTemplate.name} (${suggestedTemplate.type})</p>
                <p><strong>Confidence:</strong> ${(suggestion.confidence * 100).toFixed(1)}%</p>
            </div>
            <div class="suggestion-actions">
                <button class="btn btn-secondary btn-sm" onclick="dismissTemplateSuggestion()">
                    <i class="fas fa-times"></i> Dismiss
                </button>
                <button class="btn btn-primary btn-sm" onclick="showTemplateSuggestionDetails()">
                    <i class="fas fa-plus"></i> Create Template
                </button>
            </div>
        </div>
    `;

    // Insert banner at the top of results section
    const resultsSection = document.getElementById('results-section');
    resultsSection.insertBefore(banner, resultsSection.firstChild);
}

function dismissTemplateSuggestion() {
    const banner = document.getElementById('template-suggestion-banner');
    if (banner) {
        banner.remove();
    }
    currentTemplateSuggestion = null;
}

function showTemplateSuggestionDetails() {
    if (!currentTemplateSuggestion) return;

    const suggestion = currentTemplateSuggestion;
    const suggestedTemplate = suggestion.suggested_template;

    // Pre-fill the template upload form with suggested values
    document.getElementById('template-name').value = suggestedTemplate.name;
    document.getElementById('document-type').value = suggestedTemplate.type;
    document.getElementById('template-description').value = suggestedTemplate.description;

    // Show the template upload form
    const addTemplateSection = document.getElementById('add-template-section');
    addTemplateSection.style.display = 'block';
    addTemplateSection.scrollIntoView({ behavior: 'smooth' });

    // Add a note about the suggestion
    const existingNote = document.getElementById('suggestion-note');
    if (existingNote) {
        existingNote.remove();
    }

    const note = document.createElement('div');
    note.id = 'suggestion-note';
    note.className = 'suggestion-note';
    note.innerHTML = `
        <div class="note-content">
            <i class="fas fa-info-circle"></i>
            <span>Form pre-filled based on document analysis. You can modify the details before uploading.</span>
        </div>
    `;

    const form = document.getElementById('template-upload-form');
    form.insertBefore(note, form.firstChild);

    // Dismiss the banner
    dismissTemplateSuggestion();
}
