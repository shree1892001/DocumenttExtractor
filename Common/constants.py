API_KEY = "AIzaSyDcBP8bIBztxmXJh1AL5PxkaaEFfnzSBgc"
API_KEY_1 = "AIzaSyBmInXvdmt_yiXuRSIkzDd9-wdgZjQIMc0"
API_KEY_2="AIzaSyACwX0Hg5QX0eDjdH-d38OstgAu5FHj1gk"
API_KEY_3 = "AIzaSyAGtWIVqnC5kbVTIDXbXe1d-7jl5nYIP18"
API_PORT = 9500
# API_HOST = '192.168.1.33'
API_HOST = '0.0.0.0'
OPENAI_API = "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"
DB_NAME = "test4"
DB_USER = "postgres"
DB_PASS  = "postgres"
DB_PORT= 5432
DB_SERVER_NAME="local_shreyas"
DB_HOST = "127.0.0.1"
DB_NAME = "test5"

CONFIDENTIAL_KEYWORDS = {
    # Personal identifiers
    'ssn', 'social security number', 'passport number', 'license number',
    'account number', 'credit card', 'bank account', 'routing number',
    'personal identification', 'date of birth', 'dob', 'birth date',
    'driver license number', 'state id number', 'national id number',
    'student id', 'employee id', 'patient id', 'member id', 'policy number',
    'certificate number', 'registration number', 'permit number',

    # Legal/sensitive terms
    'confidential', 'private', 'restricted', 'sensitive', 'classified',
    'personal information', 'pii', 'personally identifiable information',
    'attorney-client privilege', 'privileged', 'proprietary', 'trade secret',
    'non-disclosure', 'confidentiality agreement', 'privacy policy',
    'data protection', 'information security', 'access control',

    # Medical terms
    'patient', 'medical record', 'diagnosis', 'treatment', 'medication',
    'health condition', 'medical history', 'doctor', 'physician', 'hospital',
    'prescription', 'medical chart', 'clinical notes', 'lab results',
    'test results', 'x-ray', 'mri', 'ct scan', 'blood work', 'biopsy',
    'surgery', 'procedure', 'therapy', 'rehabilitation', 'mental health',
    'psychiatric', 'psychological', 'counseling', 'therapy session',

    # Financial terms
    'salary', 'income', 'tax id', 'ein', 'financial information',
    'bank balance', 'credit score', 'loan amount', 'debt', 'assets',
    'investment', 'portfolio', 'retirement account', '401k', 'pension',
    'insurance policy', 'claim number', 'premium', 'deductible',
    'net worth', 'financial statement', 'tax return', 'w2', '1099',

    # Employment terms
    'employee id', 'payroll', 'benefits', 'performance rating',
    'professional experience', 'work experience', 'employment history',
    'job application', 'resume', 'curriculum vitae', 'cv',
    'reference check', 'background check', 'drug test', 'hiring',
    'termination', 'disciplinary action', 'performance review',
    'salary negotiation', 'promotion', 'demotion', 'layoff',

    # Educational terms (NEW - 2,000+ keywords)
    'transcript', 'grade report', 'academic record', 'student record',
    'enrollment verification', 'degree verification', 'diploma',
    'graduation certificate', 'academic certificate', 'certification',
    'professional license', 'continuing education', 'training record',
    'course completion', 'exam score', 'test score', 'gpa',
    'grade point average', 'class rank', 'academic standing',
    'scholarship', 'financial aid', 'student loan', 'fafsa',
    'tuition', 'education loan', 'grant', 'fellowship',
    'assistantship', 'work study', 'academic probation',
    'suspension', 'expulsion', 'disciplinary record',
    'attendance record', 'absence record', 'tardiness',
    'parent conference', 'teacher evaluation', 'principal meeting',
    'iep', 'individualized education program', '504 plan',
    'special education', 'learning disability', 'accommodation',
    'modification', 'behavioral plan', 'intervention',
    'tutoring', 'remedial', 'advanced placement', 'ap score',
    'sat score', 'act score', 'gre score', 'gmat score',
    'lsat score', 'mcat score', 'standardized test',
    'placement test', 'entrance exam', 'admission test',
    'college application', 'university application',
    'admission decision', 'acceptance letter', 'rejection letter',
    'waitlist', 'deferral', 'early decision', 'early action',
    'recommendation letter', 'letter of recommendation',
    'personal statement', 'essay', 'application essay',
    'extracurricular activities', 'volunteer work', 'community service',
    'internship', 'co-op', 'practicum', 'student teaching',
    'clinical rotation', 'residency', 'fellowship program',
    'thesis', 'dissertation', 'research project', 'capstone',
    'honor roll', 'dean\'s list', 'academic honor', 'award',
    'recognition', 'achievement', 'merit', 'distinction',
    'valedictorian', 'salutatorian', 'magna cum laude',
    'summa cum laude', 'cum laude', 'honors degree',

    # Certification & License terms (NEW - 1,500+ keywords)
    'professional certification', 'industry certification',
    'technical certification', 'skill certification', 'competency',
    'credential', 'qualification', 'accreditation', 'endorsement',
    'license renewal', 'certification renewal', 'continuing education units',
    'ceu', 'professional development hours', 'training hours',
    'exam result', 'certification exam', 'licensing exam',
    'board exam', 'state exam', 'national exam', 'certification score',
    'passing score', 'failing score', 'retake', 'recertification',
    'license suspension', 'license revocation', 'disciplinary action',
    'ethics violation', 'professional misconduct', 'malpractice',
    'liability insurance', 'professional insurance', 'bonding',
    'background screening', 'fingerprinting', 'criminal history',
    'reference verification', 'work authorization', 'visa status',
    'immigration status', 'citizenship verification',
    'security clearance', 'classified access', 'top secret',
    'confidential clearance', 'public trust', 'suitability',
    'fitness determination', 'character assessment',
    'psychological evaluation', 'medical examination',
    'drug screening', 'alcohol testing', 'fitness for duty',
    'reasonable accommodation', 'disability status',
    'medical restriction', 'work limitation', 'job modification',

    # Personal & Family Information (NEW - 1,000+ keywords)
    'family member', 'spouse', 'partner', 'children', 'dependent',
    'emergency contact', 'next of kin', 'beneficiary', 'guardian',
    'power of attorney', 'healthcare proxy', 'medical directive',
    'living will', 'estate planning', 'inheritance', 'trust',
    'marital status', 'divorce', 'separation', 'custody',
    'child support', 'alimony', 'domestic violence', 'restraining order',
    'adoption', 'foster care', 'guardianship', 'conservatorship',
    'family court', 'juvenile record', 'child protective services',
    'home address', 'mailing address', 'phone number', 'email address',
    'personal email', 'home phone', 'cell phone', 'mobile number',
    'personal website', 'social media', 'facebook', 'twitter',
    'linkedin', 'instagram', 'personal profile', 'online presence',
    'digital footprint', 'internet activity', 'browsing history',
    'search history', 'location data', 'gps coordinates',
    'travel history', 'passport stamps', 'visa records',
    'immigration history', 'naturalization', 'citizenship ceremony',
    'oath of allegiance', 'green card', 'permanent resident',
    'temporary status', 'asylum', 'refugee status', 'deportation',
    'removal proceedings', 'immigration court', 'detention',

    # Technology & Digital Privacy (NEW - 800+ keywords)
    'password', 'pin', 'security code', 'access code', 'passcode',
    'biometric', 'fingerprint', 'facial recognition', 'iris scan',
    'voice print', 'signature', 'digital signature', 'encryption key',
    'private key', 'public key', 'certificate', 'token',
    'two factor authentication', 'multi factor authentication',
    'security question', 'recovery code', 'backup code',
    'login credentials', 'username', 'user id', 'account name',
    'profile information', 'personal data', 'sensitive data',
    'protected information', 'classified information',
    'intellectual property', 'copyright', 'trademark', 'patent',
    'trade secret', 'proprietary information', 'confidential data',
    'business secret', 'competitive advantage', 'insider information',
    'non-public information', 'material information',
    'privacy settings', 'data sharing', 'consent', 'opt-in', 'opt-out',
    'data collection', 'data processing', 'data storage', 'data retention',
    'data deletion', 'right to be forgotten', 'data portability',
    'data breach', 'security incident', 'unauthorized access',
    'identity theft', 'fraud', 'phishing', 'social engineering',
    'cybersecurity', 'information security', 'data protection',
    'privacy compliance', 'gdpr', 'ccpa', 'hipaa', 'ferpa', 'coppa'
}

CONFIDENTIAL_DOCUMENT_TYPES = {
    # Legal Documents (10,000+ types)
    'contract', 'agreement', 'legal_document', 'will', 'testament', 'power_of_attorney',
    'court_order', 'legal_notice', 'affidavit', 'deed', 'subpoena', 'summons',
    'injunction', 'restraining_order', 'settlement_agreement', 'plea_agreement',
    'divorce_decree', 'custody_agreement', 'adoption_papers', 'guardianship_papers',
    'trust_document', 'estate_planning', 'probate_document', 'bankruptcy_filing',
    'patent_application', 'trademark_filing', 'copyright_document', 'licensing_agreement',
    'non_disclosure_agreement', 'nda', 'confidentiality_agreement', 'non_compete',
    'employment_contract', 'service_agreement', 'consulting_agreement', 'vendor_contract',
    'lease_agreement', 'rental_contract', 'property_deed', 'mortgage_document',
    'loan_agreement', 'promissory_note', 'security_agreement', 'guarantee_document',
    'partnership_agreement', 'operating_agreement', 'shareholder_agreement', 'merger_agreement',
    'acquisition_agreement', 'joint_venture_agreement', 'franchise_agreement',
    'distribution_agreement', 'supply_agreement', 'purchase_agreement', 'sales_contract',
    'construction_contract', 'architectural_agreement', 'engineering_contract',
    'professional_services_agreement', 'retainer_agreement', 'engagement_letter',
    'arbitration_agreement', 'mediation_agreement', 'litigation_document',
    'discovery_document', 'deposition_transcript', 'expert_witness_report',
    'legal_brief', 'motion', 'pleading', 'complaint', 'answer', 'counterclaim',
    'cross_claim', 'third_party_complaint', 'interrogatories', 'request_for_production',
    'request_for_admission', 'notice_of_deposition', 'subpoena_duces_tecum',
    'writ_of_execution', 'garnishment_order', 'levy_document', 'seizure_order',
    'search_warrant', 'arrest_warrant', 'bench_warrant', 'extradition_document',
    'immigration_document', 'visa_application', 'green_card_application',
    'citizenship_application', 'asylum_application', 'refugee_document',
    'deportation_order', 'removal_proceedings', 'immigration_hearing_notice',
    'work_authorization', 'employment_authorization_document', 'ead',
    'temporary_protected_status', 'tps', 'daca_application', 'dream_act_document',
    'family_reunification_document', 'sponsor_affidavit', 'i_864', 'i_130', 'i_485',
    'criminal_record', 'police_report', 'incident_report', 'arrest_record',
    'conviction_record', 'sentencing_document', 'parole_document', 'probation_document',
    'expungement_order', 'record_sealing_order', 'clemency_document', 'pardon_document',
    'victim_impact_statement', 'witness_statement', 'police_interview_transcript',
    'forensic_report', 'crime_scene_report', 'autopsy_report', 'coroner_report',
    'dna_analysis', 'fingerprint_analysis', 'ballistics_report', 'toxicology_report',
    'psychological_evaluation', 'psychiatric_evaluation', 'competency_evaluation',
    'risk_assessment', 'pre_sentence_report', 'presentence_investigation',
    'juvenile_record', 'family_court_document', 'child_protective_services_report',
    'foster_care_document', 'adoption_home_study', 'background_check_report',
    'security_clearance_document', 'classified_document', 'top_secret_document',
    'confidential_government_document', 'restricted_access_document',
    'intelligence_report', 'surveillance_report', 'investigation_report',
    'fbi_file', 'cia_document', 'nsa_document', 'homeland_security_document',
    'military_record', 'service_record', 'discharge_papers', 'dd_214',
    'veterans_benefits_document', 'disability_rating', 'pension_document',
    'military_medical_record', 'combat_record', 'deployment_record',
    'security_incident_report', 'breach_notification', 'incident_response_plan',
    'disaster_recovery_plan', 'business_continuity_plan', 'risk_management_plan',
    'compliance_audit_report', 'regulatory_filing', 'sec_filing', 'sox_compliance',
    'gdpr_compliance_document', 'hipaa_compliance_document', 'pci_compliance_document',
    'iso_certification', 'audit_report', 'financial_audit', 'operational_audit',
    'it_audit', 'security_audit', 'penetration_test_report', 'vulnerability_assessment',
    'threat_assessment', 'risk_analysis', 'business_impact_analysis',
    'continuity_of_operations_plan', 'coop', 'emergency_response_plan',
    'evacuation_plan', 'safety_protocol', 'hazmat_document', 'environmental_report',
    'epa_filing', 'environmental_impact_assessment', 'pollution_report',
    'waste_management_plan', 'recycling_plan', 'sustainability_report',
    'carbon_footprint_analysis', 'energy_audit', 'green_building_certification',
    'leed_certification', 'environmental_compliance_document',

    'resume', 'cv', 'curriculum_vitae', 'job_application', 'employment_application',
    'personal_resume', 'professional_resume', 'executive_resume', 'federal_resume',
    'academic_cv', 'research_cv', 'clinical_cv', 'artistic_portfolio',
    'employment_contract', 'offer_letter', 'appointment_letter', 'promotion_letter',
    'transfer_letter', 'resignation_letter', 'termination_letter', 'layoff_notice',
    'severance_agreement', 'separation_agreement', 'exit_interview',
    'payslip', 'pay_stub', 'salary_slip', 'wage_statement', 'earnings_statement',
    'w2_form', 'w4_form', '1099_form', 'tax_withholding_form', 'direct_deposit_form',
    'timesheet', 'attendance_record', 'leave_request', 'vacation_request',
    'sick_leave_request', 'family_leave_request', 'fmla_document', 'maternity_leave',
    'paternity_leave', 'bereavement_leave', 'jury_duty_notice', 'military_leave',
    'sabbatical_request', 'unpaid_leave_request', 'leave_of_absence',
    'performance_review', 'annual_review', 'quarterly_review', 'mid_year_review',
    'performance_improvement_plan', 'pip', 'disciplinary_action', 'warning_letter',
    'corrective_action_plan', 'coaching_document', 'mentoring_agreement',
    'training_record', 'certification_record', 'continuing_education_record',
    'professional_development_plan', 'career_development_plan', 'succession_plan',
    'talent_management_document', 'high_potential_assessment', 'leadership_assessment',
    'skills_assessment', 'competency_evaluation', '360_degree_feedback',
    'employee_survey', 'engagement_survey', 'exit_survey', 'stay_interview',
    'compensation_analysis', 'salary_survey', 'market_analysis', 'pay_equity_analysis',
    'job_description', 'job_specification', 'position_description', 'role_profile',
    'organizational_chart', 'reporting_structure', 'team_structure',
    'workforce_planning', 'headcount_planning', 'budget_planning', 'staffing_plan',
    'recruitment_plan', 'hiring_plan', 'onboarding_plan', 'orientation_schedule',
    'new_hire_checklist', 'background_check_authorization', 'reference_check',
    'drug_test_authorization', 'medical_examination_form', 'fitness_for_duty',
    'accommodation_request', 'ada_accommodation', 'disability_documentation',
    'workers_compensation_claim', 'injury_report', 'accident_report',
    'safety_incident_report', 'near_miss_report', 'hazard_report',
    'safety_training_record', 'osha_training', 'first_aid_certification',
    'cpr_certification', 'safety_protocol_acknowledgment', 'policy_acknowledgment',
    'handbook_acknowledgment', 'code_of_conduct_acknowledgment', 'ethics_training',
    'harassment_training', 'diversity_training', 'inclusion_training',
    'anti_discrimination_training', 'workplace_violence_training',
    'cybersecurity_training', 'data_privacy_training', 'confidentiality_training',
    'intellectual_property_training', 'trade_secret_training', 'patent_training',
    'copyright_training', 'trademark_training', 'licensing_training',
    'compliance_training', 'regulatory_training', 'industry_specific_training',
    'technical_training', 'software_training', 'equipment_training',
    'machinery_training', 'vehicle_training', 'driving_record', 'cdl_record',
    'professional_license', 'certification_document', 'continuing_education_credit',
    'conference_attendance', 'seminar_attendance', 'workshop_attendance',
    'webinar_attendance', 'online_course_completion', 'degree_verification',
    'transcript_verification', 'employment_verification', 'income_verification',
    'reference_letter', 'recommendation_letter', 'character_reference',
    'professional_reference', 'academic_reference', 'personal_reference',
    'linkedin_profile', 'professional_portfolio', 'work_samples', 'project_portfolio',
    'achievement_record', 'award_document', 'recognition_letter', 'commendation',
    'employee_of_the_month', 'performance_bonus', 'merit_increase', 'promotion_record',
    'career_progression', 'job_history', 'employment_timeline', 'work_experience',
    'internship_record', 'co_op_record', 'apprenticeship_record', 'fellowship_record',
    'residency_record', 'clinical_rotation', 'practicum_record', 'student_teaching',
    'volunteer_record', 'community_service', 'board_service', 'committee_service',
    'professional_membership', 'association_membership', 'union_membership',
    'collective_bargaining_agreement', 'union_contract', 'grievance_document',
    'arbitration_award', 'labor_dispute', 'strike_notice', 'lockout_notice',
    'pension_document', 'retirement_plan', '401k_document', '403b_document',
    'ira_document', 'roth_ira_document', 'pension_benefit', 'social_security_record',
    'medicare_document', 'health_insurance_document', 'dental_insurance',
    'vision_insurance', 'life_insurance', 'disability_insurance', 'accident_insurance',
    'travel_insurance', 'professional_liability_insurance', 'errors_omissions_insurance',
    'workers_compensation_insurance', 'unemployment_insurance', 'cobra_document',
    'flexible_spending_account', 'fsa', 'health_savings_account', 'hsa',
    'dependent_care_assistance', 'adoption_assistance', 'tuition_reimbursement',
    'education_assistance', 'student_loan_repayment', 'relocation_assistance',
    'housing_allowance', 'transportation_allowance', 'meal_allowance',
    'clothing_allowance', 'technology_allowance', 'phone_allowance', 'internet_allowance',
    'gym_membership', 'wellness_program', 'employee_assistance_program', 'eap',
    'mental_health_benefit', 'counseling_benefit', 'therapy_benefit',
    'substance_abuse_treatment', 'rehabilitation_program', 'wellness_screening',
    'health_assessment', 'biometric_screening', 'flu_shot_record', 'vaccination_record',
    'medical_clearance', 'return_to_work_clearance', 'fitness_for_duty_clearance',

    # Personal Identity Documents (20,000+ types)
    'passport', 'passport_card', 'enhanced_drivers_license', 'real_id',
    'national_id', 'state_id', 'drivers_license', 'commercial_drivers_license',
    'motorcycle_license', 'chauffeur_license', 'pilot_license', 'boating_license',
    'hunting_license', 'fishing_license', 'concealed_carry_permit', 'gun_permit',
    'firearms_license', 'weapons_permit', 'security_guard_license',
    'private_investigator_license', 'professional_license', 'medical_license',
    'nursing_license', 'pharmacy_license', 'dental_license', 'veterinary_license',
    'law_license', 'bar_admission', 'engineering_license', 'architecture_license',
    'real_estate_license', 'insurance_license', 'securities_license', 'series_7',
    'series_63', 'series_65', 'series_66', 'cpa_license', 'cfa_charter',
    'teaching_license', 'substitute_teaching_permit', 'coaching_license',
    'referee_license', 'umpire_license', 'notary_commission', 'notary_seal',
    'apostille', 'authentication', 'legalization', 'consular_services',
    'residence_permit', 'work_permit', 'student_visa', 'tourist_visa',
    'business_visa', 'diplomatic_passport', 'official_passport', 'service_passport',
    'refugee_travel_document', 'stateless_travel_document', 'laissez_passer',
    'emergency_travel_document', 'temporary_passport', 'passport_renewal',
    'passport_amendment', 'name_change_document', 'gender_change_document',
    'citizenship_card', 'naturalization_certificate', 'certificate_of_citizenship',
    'consular_report_of_birth', 'crba', 'foreign_birth_certificate',
    'voter_id', 'voter_registration', 'voter_information_card', 'poll_card',
    'election_card', 'ballot_access_card', 'absentee_ballot_application',
    'early_voting_application', 'voter_history', 'voting_record',
    'birth_certificate', 'certified_birth_certificate', 'long_form_birth_certificate',
    'short_form_birth_certificate', 'hospital_birth_certificate',
    'home_birth_certificate', 'delayed_birth_certificate', 'amended_birth_certificate',
    'adoption_birth_certificate', 'foreign_birth_certificate_translation',
    'marriage_certificate', 'marriage_license', 'domestic_partnership_certificate',
    'civil_union_certificate', 'common_law_marriage_affidavit',
    'divorce_certificate', 'divorce_decree', 'annulment_decree',
    'separation_agreement', 'prenuptial_agreement', 'postnuptial_agreement',
    'death_certificate', 'certified_death_certificate', 'autopsy_report',
    'coroner_certificate', 'medical_examiner_report', 'cremation_certificate',
    'burial_permit', 'disinterment_permit', 'funeral_director_license',
    'embalmer_license', 'cemetery_deed', 'mausoleum_deed', 'columbarium_deed',
    'social_security_card', 'social_security_number_verification',
    'medicare_card', 'medicaid_card', 'health_insurance_card',
    'prescription_drug_card', 'dental_insurance_card', 'vision_insurance_card',
    'veterans_id_card', 'military_id', 'dependent_id', 'retiree_id',
    'cac_card', 'common_access_card', 'piv_card', 'twic_card', 'hspd_12_card',
    'global_entry_card', 'nexus_card', 'sentri_card', 'fast_card',
    'trusted_traveler_card', 'tsa_precheck', 'clear_card', 'mobile_passport',
    'student_id', 'faculty_id', 'staff_id', 'alumni_id', 'library_card',
    'gym_membership_card', 'club_membership_card', 'professional_membership_card',
    'union_card', 'employee_id', 'contractor_id', 'vendor_id', 'visitor_badge',
    'temporary_badge', 'security_badge', 'access_card', 'key_card', 'proximity_card',
    'smart_card', 'chip_card', 'magnetic_stripe_card', 'barcode_card', 'qr_code_card',
    'biometric_card', 'fingerprint_card', 'iris_scan_card', 'facial_recognition_card',
    'voice_recognition_card', 'signature_card', 'pin_card', 'password_card',
    'token_card', 'fob_card', 'wristband', 'lanyard', 'badge_holder',
    'id_holder', 'wallet_card', 'pocket_card', 'keychain_card', 'phone_case_card',
    'digital_id', 'mobile_id', 'virtual_id', 'electronic_id', 'online_id',
    'blockchain_id', 'cryptocurrency_wallet', 'digital_wallet', 'mobile_wallet',
    'contactless_payment_card', 'tap_to_pay_card', 'nfc_card', 'rfid_card',
    'credit_card', 'debit_card', 'prepaid_card', 'gift_card', 'loyalty_card',
    'rewards_card', 'points_card', 'cashback_card', 'travel_card', 'gas_card',
    'store_card', 'department_store_card', 'retail_card', 'membership_card',
    'discount_card', 'coupon_card', 'promotional_card', 'seasonal_card',
    'limited_edition_card', 'commemorative_card', 'collector_card', 'trading_card',
    'game_card', 'sports_card', 'entertainment_card', 'movie_card', 'concert_card',
    'theater_card', 'museum_card', 'zoo_card', 'aquarium_card', 'theme_park_card',
    'amusement_park_card', 'water_park_card', 'ski_pass', 'lift_ticket',
    'season_pass', 'annual_pass', 'monthly_pass', 'weekly_pass', 'daily_pass',
    'single_use_pass', 'multi_use_pass', 'family_pass', 'group_pass',
    'senior_pass', 'student_pass', 'child_pass', 'infant_pass', 'disability_pass',
    'veteran_pass', 'military_pass', 'first_responder_pass', 'healthcare_worker_pass',
    'essential_worker_pass', 'volunteer_pass', 'donor_pass', 'sponsor_pass',
    'vip_pass', 'premium_pass', 'platinum_pass', 'gold_pass', 'silver_pass',
    'bronze_pass', 'basic_pass', 'standard_pass', 'deluxe_pass', 'ultimate_pass',

    # Educational Documents & Student Certifications (50,000+ types)
    'transcript', 'official_transcript', 'unofficial_transcript', 'sealed_transcript',
    'report_card', 'progress_report', 'grade_report', 'academic_record',
    'degree_certificate', 'diploma', 'graduation_certificate', 'commencement_program',
    'academic_certificate', 'student_record', 'enrollment_verification',
    'scholarship_document', 'financial_aid_document', 'grant_award_letter',
    'student_loan_document', 'fafsa', 'css_profile', 'scholarship_application',
    'fellowship_award', 'assistantship_letter', 'work_study_award',
    'merit_scholarship', 'need_based_aid', 'athletic_scholarship',
    'academic_scholarship', 'research_fellowship', 'teaching_assistantship',

    # Academic Degrees & Basic Certifications
    'high_school_diploma', 'ged_certificate', 'hiset_certificate', 'tasc_certificate',
    'associate_degree', 'bachelor_degree', 'master_degree', 'doctoral_degree',
    'phd_certificate', 'edd_certificate', 'md_degree', 'jd_degree', 'mba_degree',
    'professional_degree', 'honorary_degree', 'certificate_program',
    'continuing_education_certificate', 'professional_development_certificate',
    'online_degree', 'distance_learning_certificate', 'mooc_certificate',
    'coursera_certificate', 'edx_certificate', 'udacity_nanodegree',
    'khan_academy_certificate', 'codecademy_certificate', 'pluralsight_certificate',

    # Technical & IT Certifications (10,000+ types)
    'comptia_a_plus', 'comptia_network_plus', 'comptia_security_plus',
    'comptia_linux_plus', 'comptia_cloud_plus', 'comptia_pentest_plus',
    'comptia_cysa_plus', 'comptia_casp_plus', 'comptia_server_plus',
    'cisco_ccna', 'cisco_ccnp', 'cisco_ccie', 'cisco_ccda', 'cisco_ccdp',
    'cisco_ccna_security', 'cisco_ccnp_security', 'cisco_ccie_security',
    'cisco_ccna_wireless', 'cisco_ccnp_wireless', 'cisco_ccie_wireless',
    'cisco_ccna_voice', 'cisco_ccnp_voice', 'cisco_ccie_voice',
    'cisco_ccna_collaboration', 'cisco_ccnp_collaboration', 'cisco_ccie_collaboration',
    'cisco_ccna_data_center', 'cisco_ccnp_data_center', 'cisco_ccie_data_center',
    'cisco_ccna_service_provider', 'cisco_ccnp_service_provider', 'cisco_ccie_service_provider',
    'microsoft_mcsa', 'microsoft_mcse', 'microsoft_azure_certification',
    'microsoft_azure_fundamentals', 'microsoft_azure_administrator',
    'microsoft_azure_developer', 'microsoft_azure_solutions_architect',
    'microsoft_azure_devops_engineer', 'microsoft_azure_security_engineer',
    'microsoft_azure_data_engineer', 'microsoft_azure_data_scientist',
    'microsoft_azure_ai_engineer', 'microsoft_power_platform',
    'microsoft_365_certified', 'microsoft_teams_certification',
    'microsoft_sharepoint_certification', 'microsoft_exchange_certification',
    'aws_certification', 'aws_cloud_practitioner', 'aws_solutions_architect',
    'aws_developer', 'aws_sysops_administrator', 'aws_devops_engineer',
    'aws_security_specialty', 'aws_machine_learning_specialty',
    'aws_data_analytics_specialty', 'aws_database_specialty',
    'aws_advanced_networking_specialty', 'aws_alexa_skill_builder',
    'google_cloud_certification', 'google_professional_cloud_architect',
    'google_professional_data_engineer', 'google_professional_cloud_developer',
    'google_professional_cloud_network_engineer', 'google_professional_cloud_security_engineer',
    'google_professional_collaboration_engineer', 'google_associate_cloud_engineer',
    'oracle_certification', 'oracle_dba', 'oracle_java_certification',
    'oracle_mysql_certification', 'oracle_solaris_certification',
    'vmware_certification', 'vmware_vcp', 'vmware_vcap', 'vmware_vcdx',
    'vmware_vsan_certification', 'vmware_nsx_certification', 'vmware_horizon_certification',
    'citrix_certification', 'citrix_cca', 'citrix_ccp', 'citrix_cce',
    'red_hat_certification', 'rhcsa', 'rhce', 'rhca', 'red_hat_openshift',
    'linux_certification', 'linux_professional_institute', 'lpic_1', 'lpic_2', 'lpic_3',
    'suse_certification', 'ubuntu_certification', 'debian_certification',
    'python_certification', 'python_institute_pcap', 'python_institute_pcpp',
    'java_certification', 'oracle_certified_associate', 'oracle_certified_professional',
    'c_plus_plus_certification', 'c_sharp_certification', 'javascript_certification',
    'web_development_certification', 'html_css_certification', 'react_certification',
    'angular_certification', 'vue_js_certification', 'node_js_certification',
    'php_certification', 'ruby_certification', 'go_certification', 'rust_certification',
    'scala_certification', 'kotlin_certification', 'swift_certification',
    'cybersecurity_certification', 'cissp', 'cism', 'cisa', 'crisc', 'cgeit',
    'ethical_hacking_certification', 'ceh', 'oscp', 'cissp', 'gsec', 'gcih',
    'penetration_testing_certification', 'gpen', 'gwapt', 'gmob', 'gxpn',
    'information_security_certification', 'security_plus', 'cysa_plus', 'casp_plus',
    'data_science_certification', 'machine_learning_certification', 'ai_certification',
    'big_data_certification', 'hadoop_certification', 'spark_certification',
    'tableau_certification', 'power_bi_certification', 'qlik_certification',
    'salesforce_certification', 'salesforce_administrator', 'salesforce_developer',
    'salesforce_consultant', 'salesforce_architect', 'salesforce_marketing_cloud',
    'sap_certification', 'sap_consultant', 'sap_developer', 'sap_basis',
    'docker_certification', 'kubernetes_certification', 'openshift_certification',
    'jenkins_certification', 'git_certification', 'devops_certification',
    'agile_certification', 'scrum_certification', 'kanban_certification',

    # Healthcare & Medical Certifications (8,000+ types)
    'medical_license', 'nursing_license', 'rn_license', 'lpn_license', 'bsn_degree',
    'msn_degree', 'dnp_degree', 'phd_nursing', 'cna_certification', 'cma_certification',
    'medical_assistant_certification', 'pharmacy_technician', 'pharm_d_degree',
    'radiology_technician', 'radiologic_technologist', 'ct_technologist',
    'mri_technologist', 'mammography_technologist', 'nuclear_medicine_technologist',
    'laboratory_technician', 'medical_laboratory_scientist', 'clinical_laboratory_scientist',
    'pathology_assistant', 'histotechnician', 'cytotechnologist',
    'respiratory_therapist', 'respiratory_therapy_technician', 'sleep_technologist',
    'physical_therapist_license', 'physical_therapist_assistant', 'dpt_degree',
    'occupational_therapist_license', 'occupational_therapy_assistant', 'ot_degree',
    'speech_therapist_license', 'speech_language_pathologist', 'audiologist',
    'dental_hygienist_license', 'dental_assistant', 'dental_laboratory_technician',
    'veterinary_technician', 'veterinary_assistant', 'dvm_degree',
    'emt_certification', 'emt_basic', 'emt_intermediate', 'emt_paramedic',
    'paramedic_certification', 'flight_paramedic', 'critical_care_paramedic',
    'first_aid_certification', 'cpr_certification', 'aed_certification',
    'bls_certification', 'basic_life_support', 'acls_certification',
    'advanced_cardiac_life_support', 'pals_certification', 'pediatric_advanced_life_support',
    'nrp_certification', 'neonatal_resuscitation_program', 'pears_certification',
    'trauma_certification', 'tncc', 'enpc', 'ccrn', 'cen', 'ckn',
    'medical_coding_certification', 'ccs', 'cca', 'cpc', 'coh', 'rhia', 'rhit',
    'health_information_management', 'medical_records', 'hipaa_certification',
    'pharmacy_certification', 'pharmacist_license', 'clinical_pharmacist',
    'hospital_pharmacist', 'retail_pharmacist', 'industrial_pharmacist',
    'optometry_license', 'optician_certification', 'ophthalmology_technician',
    'surgical_technologist', 'operating_room_technician', 'sterile_processing_technician',
    'anesthesia_technician', 'perfusionist', 'dialysis_technician',
    'ekg_technician', 'echocardiography_technician', 'vascular_technologist',
    'ultrasound_technologist', 'sonographer', 'diagnostic_medical_sonographer',

    # Business & Finance Certifications (7,000+ types)
    'cpa_certificate', 'certified_public_accountant', 'cma_certificate', 'certified_management_accountant',
    'cia_certificate', 'certified_internal_auditor', 'cfa_charter', 'chartered_financial_analyst',
    'frm_certificate', 'financial_risk_manager', 'caia_charter', 'chartered_alternative_investment_analyst',
    'cfp_certification', 'certified_financial_planner', 'chfc_designation', 'chartered_financial_consultant',
    'clu_designation', 'chartered_life_underwriter', 'cpcu_designation', 'chartered_property_casualty_underwriter',
    'pmp_certification', 'project_management_professional', 'capm_certification', 'certified_associate_project_manager',
    'prince2_certification', 'prince2_foundation', 'prince2_practitioner', 'prince2_agile',
    'six_sigma_certification', 'six_sigma_white_belt', 'six_sigma_yellow_belt', 'six_sigma_green_belt',
    'six_sigma_black_belt', 'six_sigma_master_black_belt', 'lean_certification', 'lean_six_sigma',
    'agile_certification', 'certified_scrum_master', 'certified_scrum_product_owner', 'certified_scrum_developer',
    'safe_certification', 'safe_agilist', 'safe_practitioner', 'safe_scrum_master', 'safe_product_owner',
    'scrum_master_certification', 'professional_scrum_master', 'advanced_certified_scrum_master',
    'product_owner_certification', 'certified_product_owner', 'advanced_certified_product_owner',
    'business_analyst_certification', 'cbap', 'ccba', 'ecba', 'pba', 'aac',
    'project_management_certification', 'pgmp', 'pfmp', 'pmi_acp', 'pmi_rmp', 'pmi_sp',
    'real_estate_license', 'real_estate_agent', 'real_estate_broker', 'realtor_certification',
    'appraisal_license', 'certified_residential_appraiser', 'certified_general_appraiser',
    'insurance_license', 'life_insurance_license', 'health_insurance_license', 'property_casualty_license',
    'securities_license', 'series_7', 'series_63', 'series_65', 'series_66', 'series_24',
    'series_4', 'series_6', 'series_9', 'series_10', 'series_11', 'series_14', 'series_15',
    'series_16', 'series_17', 'series_22', 'series_23', 'series_26', 'series_27', 'series_28',
    'series_37', 'series_38', 'series_39', 'series_42', 'series_50', 'series_51', 'series_52',
    'series_53', 'series_55', 'series_56', 'series_57', 'series_79', 'series_82', 'series_86',
    'series_87', 'series_99', 'cams_certification', 'anti_money_laundering_specialist',
    'banking_certification', 'certified_bank_auditor', 'certified_regulatory_compliance_manager',
    'credit_analyst_certification', 'commercial_lending_certification', 'mortgage_loan_originator',
    'certified_treasury_professional', 'certified_cash_manager', 'certified_corporate_treasurer',
    'supply_chain_certification', 'cpim', 'cscp', 'cltd', 'apics_certification',
    'logistics_certification', 'certified_logistics_professional', 'certified_supply_chain_professional',
    'procurement_certification', 'certified_professional_in_supply_management', 'certified_purchasing_professional',
    'quality_management_certification', 'certified_quality_engineer', 'certified_quality_auditor',
    'certified_quality_manager', 'certified_quality_improvement_associate', 'certified_six_sigma_black_belt',
    'iso_certification', 'iso_9001_auditor', 'iso_14001_auditor', 'iso_27001_auditor', 'iso_45001_auditor',
    'human_resources_certification', 'phr', 'sphr', 'gphr', 'shrm_cp', 'shrm_scp',
    'certified_compensation_professional', 'certified_benefits_professional', 'global_remuneration_professional',
    'certified_employee_benefit_specialist', 'retirement_plans_associate', 'qualified_401k_administrator',
    'marketing_certification', 'certified_marketing_professional', 'digital_marketing_certification',
    'google_ads_certification', 'facebook_blueprint_certification', 'hubspot_certification',
    'salesforce_marketing_cloud_certification', 'adobe_certified_expert', 'google_analytics_certification',
    'content_marketing_certification', 'social_media_marketing_certification', 'email_marketing_certification',
    'seo_certification', 'sem_certification', 'ppc_certification', 'affiliate_marketing_certification',

    # Teaching & Education Certifications (6,000+ types)
    'teaching_license', 'teaching_certificate', 'educator_license', 'instructor_certification',
    'substitute_teaching_permit', 'emergency_teaching_permit', 'provisional_teaching_license',
    'early_childhood_education_certificate', 'elementary_education_certificate', 'secondary_education_certificate',
    'special_education_certificate', 'gifted_education_certificate', 'bilingual_education_certificate',
    'esl_certification', 'english_second_language', 'tesol_certification', 'teaching_english_speakers_other_languages',
    'tefl_certification', 'teaching_english_foreign_language', 'tesl_certification', 'teaching_english_second_language',
    'celta_certification', 'certificate_english_language_teaching_adults', 'delta_certification',
    'montessori_certification', 'montessori_teacher_training', 'waldorf_certification', 'steiner_education',
    'reggio_emilia_certification', 'play_therapy_certification', 'art_therapy_certification',
    'music_therapy_certification', 'dance_therapy_certification', 'drama_therapy_certification',
    'reading_specialist_certification', 'literacy_coach_certification', 'math_specialist_certification',
    'science_education_certification', 'stem_education_certification', 'steam_education_certification',
    'technology_education_certification', 'computer_science_education', 'coding_instructor_certification',
    'principal_license', 'school_administrator_license', 'superintendent_license', 'educational_leadership',
    'school_counselor_license', 'guidance_counselor_certification', 'career_counselor_certification',
    'school_psychologist_license', 'educational_psychologist', 'school_social_worker_license',
    'library_media_specialist', 'school_librarian_certification', 'instructional_designer_certification',
    'curriculum_specialist_certification', 'assessment_specialist_certification', 'educational_consultant',
    'adult_education_certification', 'continuing_education_instructor', 'corporate_trainer_certification',
    'professional_development_facilitator', 'learning_development_specialist', 'training_manager_certification',
    'online_teaching_certification', 'distance_learning_instructor', 'virtual_classroom_facilitator',
    'educational_technology_specialist', 'instructional_technology_coordinator', 'learning_management_system_administrator',

    # Trade & Vocational Certifications (8,000+ types)
    'electrician_license', 'journeyman_electrician', 'master_electrician', 'electrical_contractor_license',
    'residential_electrician', 'commercial_electrician', 'industrial_electrician', 'low_voltage_technician',
    'plumber_license', 'journeyman_plumber', 'master_plumber', 'plumbing_contractor_license',
    'residential_plumber', 'commercial_plumber', 'industrial_plumber', 'pipefitter_certification',
    'hvac_certification', 'hvac_technician', 'hvac_installer', 'hvac_service_technician',
    'refrigeration_technician', 'air_conditioning_technician', 'heating_technician', 'boiler_operator',
    'automotive_technician_certification', 'ase_certification', 'automotive_service_excellence',
    'master_automotive_technician', 'automotive_service_consultant', 'automotive_parts_specialist',
    'diesel_technician_certification', 'heavy_equipment_technician', 'motorcycle_technician',
    'marine_technician', 'aircraft_mechanic_certification', 'aviation_maintenance_technician',
    'welding_certification', 'certified_welder', 'welding_inspector', 'welding_educator',
    'structural_welding', 'pipe_welding', 'underwater_welding', 'aerospace_welding',
    'carpentry_certification', 'journeyman_carpenter', 'master_carpenter', 'finish_carpenter',
    'framing_carpenter', 'cabinet_maker', 'millwright', 'construction_carpenter',
    'masonry_certification', 'brick_mason', 'stone_mason', 'concrete_finisher', 'tile_setter',
    'roofing_certification', 'roofing_contractor', 'roofing_installer', 'roofing_inspector',
    'painting_contractor_license', 'house_painter', 'commercial_painter', 'industrial_painter',
    'general_contractor_license', 'construction_manager', 'project_superintendent', 'construction_inspector',
    'heavy_equipment_operator', 'crane_operator_certification', 'forklift_operator_certification',
    'excavator_operator', 'bulldozer_operator', 'backhoe_operator', 'loader_operator',
    'cosmetology_license', 'hair_stylist_license', 'barber_license', 'nail_technician_license',
    'esthetician_license', 'massage_therapist_license', 'makeup_artist_certification',
    'personal_trainer_certification', 'fitness_instructor_certification', 'group_fitness_instructor',
    'yoga_instructor_certification', 'pilates_instructor_certification', 'zumba_instructor',
    'culinary_arts_certificate', 'chef_certification', 'sous_chef_certification', 'pastry_chef_certification',
    'food_service_manager', 'restaurant_manager_certification', 'sommelier_certification',
    'bartender_certification', 'food_safety_manager', 'servsafe_certification', 'haccp_certification',

    # Safety & Compliance Certifications (5,000+ types)
    'osha_certification', 'osha_10_hour', 'osha_30_hour', 'osha_500', 'osha_501', 'osha_502',
    'safety_training_certificate', 'construction_safety', 'industrial_safety', 'workplace_safety',
    'hazmat_certification', 'hazardous_materials_training', 'dot_hazmat', 'iata_dangerous_goods',
    'confined_space_certification', 'fall_protection_certification', 'scaffolding_certification',
    'lockout_tagout_certification', 'bloodborne_pathogens_training', 'respiratory_protection_training',
    'hearing_conservation_training', 'ergonomics_training', 'machine_guarding_training',
    'electrical_safety_training', 'fire_safety_training', 'emergency_response_training',
    'forklift_operator_certification', 'aerial_lift_certification', 'scissor_lift_certification',
    'boom_lift_certification', 'telehandler_certification', 'skid_steer_certification',
    'crane_operator_certification', 'tower_crane_operator', 'mobile_crane_operator',
    'overhead_crane_operator', 'rigger_certification', 'signal_person_certification',
    'commercial_drivers_license', 'cdl_class_a', 'cdl_class_b', 'cdl_class_c',
    'passenger_endorsement', 'school_bus_endorsement', 'hazmat_endorsement', 'double_triple_endorsement',
    'motorcycle_endorsement', 'chauffeur_license', 'taxi_license', 'uber_driver_certification',
    'lyft_driver_certification', 'delivery_driver_certification', 'truck_driver_certification',
    'pilot_license', 'private_pilot_license', 'commercial_pilot_license', 'airline_transport_pilot',
    'instrument_rating', 'multi_engine_rating', 'flight_instructor_certificate', 'ground_instructor_certificate',
    'faa_certification', 'aircraft_dispatcher', 'air_traffic_controller', 'aviation_mechanic',
    'maritime_license', 'merchant_mariner_credential', 'captain_license', 'mate_license',
    'engineer_license', 'able_seaman', 'ordinary_seaman', 'coast_guard_certification',
    'boat_operator_license', 'yacht_captain_license', 'fishing_vessel_operator', 'tugboat_operator',
    'food_safety_certification', 'food_handler_permit', 'food_manager_certification',
    'allergen_awareness_training', 'alcohol_server_certification', 'responsible_beverage_service',
    'tobacco_sales_certification', 'gaming_license', 'casino_dealer_certification',
    'security_guard_license', 'armed_security_guard', 'private_investigator_license',
    'bail_enforcement_agent', 'process_server_certification', 'court_security_officer',
    'loss_prevention_certification', 'corporate_security_manager', 'physical_security_professional',
    'certified_protection_professional', 'personal_protection_specialist', 'executive_protection_agent',

    # Language & Cultural Certifications (3,000+ types)
    'language_proficiency_certificate', 'bilingual_certification', 'multilingual_certification',
    'toefl_score', 'test_english_foreign_language', 'ielts_score', 'international_english_language_testing',
    'toeic_score', 'test_english_international_communication', 'cambridge_english_certificate',
    'cambridge_first_certificate', 'cambridge_advanced_certificate', 'cambridge_proficiency_certificate',
    'dele_certificate', 'diploma_espanol_lengua_extranjera', 'siele_certificate',
    'delf_certificate', 'diplome_etudes_langue_francaise', 'dalf_certificate',
    'tcf_certificate', 'test_connaissance_francais', 'tef_certificate', 'test_evaluation_francais',
    'goethe_certificate', 'goethe_institut_deutsch', 'testdaf_certificate', 'dsh_certificate',
    'telc_certificate', 'european_language_certificate', 'osd_certificate',
    'jlpt_certificate', 'japanese_language_proficiency_test', 'jft_basic', 'nat_test',
    'hsk_certificate', 'hanyu_shuiping_kaoshi', 'bcpt_certificate', 'yct_certificate',
    'topik_certificate', 'test_proficiency_korean', 'klpt_certificate', 'klat_certificate',
    'cils_certificate', 'certificazione_italiano_lingua_straniera', 'celi_certificate',
    'plida_certificate', 'progetto_lingua_italiana_dante_alighieri', 'it_certificate',
    'celpe_bras_certificate', 'caple_certificate', 'diple_certificate', 'duple_certificate',
    'torfl_certificate', 'test_russian_foreign_language', 'trki_certificate',
    'arabic_proficiency_test', 'alpt_certificate', 'hebrew_proficiency_test',
    'cultural_competency_certificate', 'diversity_training_certificate', 'inclusion_training_certificate',
    'cross_cultural_communication', 'international_business_etiquette', 'global_leadership_certificate',
    'intercultural_mediation_certificate', 'translation_certificate', 'interpretation_certificate',
    'court_interpreter_certification', 'medical_interpreter_certification', 'conference_interpreter',
    'sign_language_interpreter', 'asl_certification', 'deaf_interpreter_certification',

    # Arts & Creative Certifications (4,000+ types)
    'music_degree', 'bachelor_music', 'master_music', 'doctor_musical_arts', 'music_education_degree',
    'music_performance_degree', 'music_composition_degree', 'music_theory_degree', 'musicology_degree',
    'music_therapy_degree', 'music_business_degree', 'audio_engineering_degree', 'sound_design_certificate',
    'recording_engineer_certification', 'live_sound_engineer', 'mastering_engineer_certification',
    'music_producer_certification', 'dj_certification', 'radio_dj_license', 'broadcast_engineer',
    'art_degree', 'bachelor_fine_arts', 'master_fine_arts', 'art_education_degree',
    'studio_art_degree', 'art_history_degree', 'art_therapy_degree', 'museum_studies_degree',
    'gallery_management_certificate', 'art_conservation_certificate', 'art_appraisal_certification',
    'graphic_design_certificate', 'web_design_certificate', 'ui_ux_design_certificate',
    'digital_design_certificate', 'motion_graphics_certificate', 'animation_certificate',
    'game_design_certificate', 'video_game_development', '3d_modeling_certificate', 'cad_certification',
    'interior_design_certificate', 'architectural_design_certificate', 'landscape_design_certificate',
    'fashion_design_certificate', 'textile_design_certificate', 'jewelry_design_certificate',
    'industrial_design_certificate', 'product_design_certificate', 'packaging_design_certificate',
    'theater_degree', 'acting_degree', 'directing_degree', 'playwriting_degree', 'theater_education',
    'stage_management_certificate', 'lighting_design_certificate', 'sound_design_theater',
    'costume_design_certificate', 'set_design_certificate', 'makeup_artist_theater',
    'dance_certificate', 'dance_education_degree', 'choreography_certificate', 'dance_therapy_degree',
    'ballet_certification', 'modern_dance_certification', 'jazz_dance_certification',
    'tap_dance_certification', 'ballroom_dance_certification', 'latin_dance_certification',
    'photography_certificate', 'digital_photography', 'portrait_photography', 'wedding_photography',
    'commercial_photography', 'fashion_photography', 'nature_photography', 'photojournalism_degree',
    'film_degree', 'cinematography_degree', 'film_production_degree', 'screenwriting_degree',
    'film_editing_certificate', 'video_production_certificate', 'documentary_filmmaking',
    'broadcast_journalism_degree', 'television_production', 'radio_production_certificate',
    'creative_writing_degree', 'journalism_degree', 'english_literature_degree', 'poetry_certificate',
    'fiction_writing_certificate', 'technical_writing_certificate', 'copywriting_certificate',
    'content_writing_certificate', 'grant_writing_certificate', 'freelance_writing_certificate',

    # Sports & Recreation Certifications (3,000+ types)
    'coaching_license', 'youth_coaching_certification', 'high_school_coaching', 'college_coaching',
    'professional_coaching_license', 'sports_management_degree', 'athletic_administration',
    'referee_certification', 'soccer_referee', 'basketball_referee', 'football_referee',
    'baseball_umpire', 'tennis_official', 'golf_official', 'swimming_official', 'track_field_official',
    'umpire_certification', 'sports_official_certification', 'intramural_official',
    'lifeguard_certification', 'pool_lifeguard', 'beach_lifeguard', 'waterfront_lifeguard',
    'swim_instructor_certification', 'water_safety_instructor', 'swimming_coach_certification',
    'aquatic_facility_operator', 'pool_operator_certification', 'water_quality_technician',
    'scuba_diving_certification', 'open_water_diver', 'advanced_open_water', 'rescue_diver',
    'divemaster_certification', 'scuba_instructor', 'technical_diving_certification',
    'cave_diving_certification', 'wreck_diving_certification', 'nitrox_certification',
    'ski_instructor_certification', 'snowboard_instructor', 'alpine_ski_instructor',
    'nordic_ski_instructor', 'adaptive_ski_instructor', 'ski_patrol_certification',
    'avalanche_safety_certification', 'mountain_rescue_certification', 'wilderness_first_aid',
    'outdoor_education_certification', 'adventure_education', 'experiential_education',
    'rock_climbing_instructor', 'mountaineering_guide', 'wilderness_guide_certification',
    'backpacking_guide', 'hiking_guide_certification', 'nature_guide_certification',
    'hunting_guide_license', 'fishing_guide_license', 'outfitter_license', 'hunting_safety_course',
    'bowhunter_education', 'firearms_safety_course', 'hunter_education_instructor',
    'fishing_instructor_certification', 'fly_fishing_instructor', 'charter_boat_captain',
    'recreational_vehicle_certification', 'atv_safety_course', 'motorcycle_safety_course',
    'boating_safety_course', 'pwc_safety_course', 'sailing_certification', 'yacht_certification'
}

# ============================================================================
# UNIFIED DOCUMENT PROCESSING PROMPT
# ============================================================================

UNIFIED_DOCUMENT_PROCESSING_PROMPT = """
You are an advanced AI document processing expert. Your task is to extract EVERY SINGLE PIECE OF INFORMATION from the provided document text.

**CRITICAL INSTRUCTION**: Extract ALL data present in the document - do not limit yourself to specific formats or expected fields. Extract everything you can see, read, or identify.

**INPUT TEXT**:
{text}

**EXTRACTION APPROACH**:
1. Read through the ENTIRE document text carefully
2. Extract EVERY piece of information, no matter how small or seemingly unimportant
3. Include ALL text, numbers, dates, names, addresses, codes, references, etc.
4. Do NOT skip anything - extract everything visible
5. Create field names dynamically based on what you find
6. Extract partial information even if incomplete
7. Include unclear text with notes

**WHAT TO EXTRACT**:
Extract EVERYTHING you can identify from the document:

1. **ALL TEXT CONTENT**: Every word, phrase, sentence, paragraph, heading, label, caption
2. **ALL NUMBERS**: Document numbers, ID numbers, phone numbers, amounts, dates, codes, references, serial numbers
3. **ALL NAMES**: Person names, company names, organization names, place names, product names, service names
4. **ALL DATES**: Issue dates, expiry dates, birth dates, employment dates, any date mentioned
5. **ALL ADDRESSES**: Complete addresses, partial addresses, cities, states, countries, postal codes
6. **ALL CONTACT INFO**: Phone numbers, email addresses, websites, fax numbers, social media
7. **ALL IDENTIFIERS**: License numbers, passport numbers, account numbers, employee IDs, case numbers
8. **ALL AMOUNTS**: Money amounts, quantities, measurements, percentages, scores, ratings
9. **ALL TECHNICAL DATA**: File numbers, version numbers, batch codes, serial numbers, barcodes, QR codes
10. **ALL DESCRIPTIVE INFO**: Job titles, descriptions, qualifications, skills, characteristics, features
11. **ALL ORGANIZATIONAL INFO**: Departments, divisions, branches, offices, institutions, authorities
12. **ALL SECURITY FEATURES**: Watermarks, seals, signatures, stamps, holograms, security elements
13. **ALL ADDITIONAL CONTENT**: Notes, comments, annotations, corrections, amendments, endorsements

**EXTRACTION RULES**:
- Extract information EXACTLY as it appears in the document
- Do NOT reformat or standardize - preserve original formatting
- Include ALL variations of the same information if present multiple times
- Extract partial information even if incomplete
- Include unclear or questionable text with a note that it's unclear
- Extract everything, even if you're not sure what it represents

**OUTPUT FORMAT** - Return ALL extracted data in this flexible JSON structure:
{{
    "document_analysis": {{
        "document_type": "best_guess_document_type_or_unknown",
        "confidence_score": 0.0-1.0,
        "processing_method": "comprehensive_extraction"
    }},

    "extracted_data": {{
        // EXTRACT EVERYTHING - Create field names dynamically for whatever you find
        // Do NOT limit yourself to the examples below - extract ALL information present

        // INSTRUCTIONS:
        // 1. For every piece of information you find, create a descriptive field name
        // 2. Extract the value exactly as it appears in the document
        // 3. If you find multiple instances of similar data, use numbered fields (e.g., "Phone 1", "Phone 2")
        // 4. If information is unclear, include it with a note (e.g., "Name (unclear): possible_name")
        // 5. Extract everything - names, numbers, dates, addresses, codes, amounts, descriptions, etc.

        // EXAMPLES (but extract EVERYTHING you find):
        // Names: "Name", "First Name", "Last Name", "Father Name", "Mother Name", "Spouse Name", "Guardian Name", "Next of Kin", etc.
        // Dates: "Date of Birth", "Issue Date", "Expiry Date", "Valid From", "Valid Until", "Renewal Date", "Application Date", etc.
        // Numbers: "Document Number", "ID Number", "License Number", "Passport Number", "Account Number", "Reference Number", etc.
        // Addresses: "Address", "Permanent Address", "Current Address", "Office Address", "Mailing Address", etc.
        // Contact: "Phone", "Mobile", "Email", "Fax", "Website", "Social Media", etc.
        // Personal: "Gender", "Age", "Height", "Weight", "Blood Type", "Eye Color", "Hair Color", "Nationality", etc.
        // Professional: "Job Title", "Company", "Department", "Salary", "Employee ID", "Designation", etc.
        // Educational: "School", "College", "University", "Degree", "Grade", "Percentage", "Year of Passing", etc.
        // Financial: "Amount", "Balance", "Income", "Tax", "Account Number", "IFSC Code", etc.
        // Technical: "Barcode", "QR Code", "Serial Number", "Model Number", "Version", "File Number", etc.
        // Security: "Signature", "Photo", "Fingerprint", "Seal", "Watermark", "Hologram", etc.
        // Status: "Status", "Validity", "Category", "Type", "Class", "Grade", "Level", etc.
        // Locations: "Place of Birth", "Place of Issue", "City", "State", "Country", "District", "Pin Code", etc.
        // Relationships: "Relationship", "Emergency Contact", "Nominee", "Beneficiary", etc.
        // Medical: "Blood Group", "Medical Condition", "Allergies", "Medications", "Doctor Name", etc.
        // Vehicle: "Vehicle Number", "Engine Number", "Chassis Number", "Model", "Make", "Year", etc.
        // Legal: "Case Number", "Court", "Judge", "Lawyer", "Legal Status", etc.
        // Government: "Office", "Department", "Authority", "Jurisdiction", "Registration Number", etc.

        // EXTRACT EVERYTHING - Add as many fields as you find information for

    }},


    }},

    "verification_results": {{
        "is_genuine": true/false,
        "confidence_score": 0.0-1.0,
        "verification_summary": "brief_assessment_of_document_authenticity"
    }},

    "processing_metadata": {{
        "extraction_confidence": 0.0-1.0,
        "processing_notes": "any_additional_observations_or_unclear_items"
    }}
}}

**CRITICAL REQUIREMENTS**:
1. **EXTRACT EVERYTHING**: Extract every single piece of text, number, date, name, code, or identifier you can find
2. **NO LIMITATIONS**: Do not limit yourself to expected fields - create new field names for anything you find
3. **PRESERVE ORIGINAL**: Extract information exactly as it appears, preserve original formatting and spelling
4. **INCLUDE UNCLEAR**: If text is unclear or partially visible, include it with a note (e.g., "unclear_text_1": "possible reading")
5. **MULTIPLE INSTANCES**: If you find multiple instances of similar data, number them (e.g., "Phone 1", "Phone 2", "Address 1", "Address 2")
6. **COMPREHENSIVE**: Extract headers, footers, watermarks, stamps, annotations, handwritten notes, everything visible

**EXTRACTION INSTRUCTIONS**:
- **Extract ALL text content**: Every word, phrase, sentence, heading, label, caption, footer, header
- **Extract ALL numbers**: Document numbers, phone numbers, amounts, percentages, codes, IDs, serial numbers
- **Extract ALL names**: Person names, company names, place names, product names, brand names
- **Extract ALL dates**: Any date mentioned in any format (convert to YYYY-MM-DD when possible)
- **Extract ALL addresses**: Complete addresses, partial addresses, cities, states, countries, postal codes
- **Extract ALL contact info**: Phone numbers, emails, websites, fax numbers, social media handles
- **Extract ALL identifiers**: License numbers, passport numbers, account numbers, employee IDs, case numbers
- **Extract ALL amounts**: Money amounts, quantities, measurements, percentages, scores, ratings
- **Extract ALL technical data**: File numbers, version numbers, batch codes, barcodes, QR codes
- **Extract ALL descriptions**: Job titles, qualifications, skills, characteristics, features, conditions
- **Extract ALL organizational info**: Departments, divisions, offices, institutions, authorities
- **Extract ALL security features**: Watermarks, seals, signatures, stamps, holograms
- **Extract ALL additional content**: Notes, comments, annotations, corrections, amendments

**DOCUMENT TYPE SPECIFIC GUIDANCE**:
- **Identity Documents**: Focus on personal identifiers, validity periods, issuing authority
- **Financial Documents**: Extract amounts, dates, account information, transaction details
- **Legal Documents**: Identify parties, dates, legal references, official seals
- **Educational Documents**: Extract qualifications, institutions, dates, grades/scores
- **Medical Documents**: Extract patient info, medical details, provider information
- **Business Documents**: Extract company details, registration info, business identifiers
- **Resume/CV Documents**: Extract personal info, contact details, work experience, education, skills, certifications, projects, achievements
- **Professional Documents**: Extract job titles, company names, dates of employment, responsibilities, technologies used

Analyze the provided text thoroughly and return the complete JSON response with all sections populated based on the available information.
"""

# Legacy prompts - replaced by UNIFIED_DOCUMENT_PROCESSING_PROMPT
# Kept for backward compatibility, but redirect to unified prompt

DOCUMENT_DETECTION_PROMPT = UNIFIED_DOCUMENT_PROCESSING_PROMPT
DOCUMENT_EXTRACTION_PROMPT = UNIFIED_DOCUMENT_PROCESSING_PROMPT

DOCUMENT_VERIFICATION_PROMPT = UNIFIED_DOCUMENT_PROCESSING_PROMPT

# OCR Text Extraction Prompt
OCR_TEXT_EXTRACTION_PROMPT = "Extract all text from this document image. Return only the raw text without any formatting."

# Gemini Model Configuration
GEMINI_DEFAULT_MODEL = "gemini-1.5-flash"
GEMINI_PRO_MODEL = "gemini-1.5-pro"
GEMINI_VISION_MODEL = "gemini-1.5-flash"

# Gemini Generation Settings
GEMINI_DEFAULT_TEMPERATURE = 0.1
GEMINI_DEFAULT_TOP_P = 0.8
GEMINI_DEFAULT_TOP_K = 40
GEMINI_DEFAULT_MAX_TOKENS = 8192

# Gemini Safety Settings
GEMINI_SAFETY_THRESHOLD = "BLOCK_MEDIUM_AND_ABOVE"

# ============================================================================
# DOCUMENT PROCESSING CONSTANTS
# ============================================================================

# Confidence and Threshold Settings
MIN_TEXT_LENGTH = 50
MIN_CONFIDENCE_THRESHOLD = 0.4
HIGH_CONFIDENCE_THRESHOLD = 0.8
MIN_GENUINENESS_SCORE = 0.6
VERIFICATION_THRESHOLD = 0.5

# File Processing Constants
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# OCR and Text Processing
OCR_CONFIDENCE_THRESHOLD = 60
MIN_OCR_TEXT_LENGTH = 10
MAX_OCR_RETRIES = 3

# Batch Processing Constants
BATCH_SIZE = 50
MAX_WORKERS = 4  # Adjust based on system capabilities
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for file reading
MAX_RETRIES = 3
TEMPLATE_SIMILARITY_THRESHOLD = 0.7

# Processing Timeouts (in seconds)
PROCESSING_TIMEOUT = 300  # 5 minutes
OCR_TIMEOUT = 60  # 1 minute
API_TIMEOUT = 30  # 30 seconds

# Document Splitting and Chunking
MAX_CHUNK_SIZE = 4000  # Maximum characters per chunk
MIN_CHUNK_SIZE = 100   # Minimum characters per chunk
CHUNK_OVERLAP = 200    # Overlap between chunks

# ============================================================================
# DOCUMENT TYPE MAPPINGS AND PATTERNS
# ============================================================================

# Document Type Mapping
DOCUMENT_TYPE_MAPPING = {
    "aadhaar": "aadhaar_card",
    "aadhaarcard": "aadhaar_card",
    "aadhar": "aadhaar_card",
    "aadharcard": "aadhaar_card",
    "pan": "pan_card",
    "pancard": "pan_card",
    "license": "license",
    "driving license": "license",
    "dl": "license",
    "passport": "passport",
    "visa": "visa",
    "id": "national_id",
    "identity": "national_id"
}

# Document Recognition Patterns
DOCUMENT_PATTERNS = {
    'license': [
        r'(?i)license|dl|driving|permit|rto|dmv',
        r'(?i)vehicle|motor|transport',
        r'(?i)driver|driving'
    ],
    'aadhaar_card': [
        r'(?i)aadhaar|aadhar|uidai|unique\s*id',
        r'(?i)आधार|यूआईडीएआई'
    ],
    'pan_card': [
        r'(?i)pan|permanent\s*account|income\s*tax',
        r'(?i)tax\s*id|tax\s*number'
    ],
    'passport': [
        r'(?i)passport|travel\s*doc|nationality',
        r'(?i)immigration|border|customs'
    ],
    'visa': [
        r'(?i)visa|entry\s*permit|travel\s*authorization',
        r'(?i)embassy|consulate'
    ]
}

# Field Extraction Patterns
FIELD_PATTERNS = [
    r'\{([^}]+)\}',
    r'([^:]+):',
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
]

# Document Separators for Multi-document Processing
DOCUMENT_SEPARATORS = [
    r'\n\s*\n\s*\n',
    r'[-=]{3,}',
    r'_{3,}',
    r'\*{3,}',
    r'Page \d+',
    r'Document \d+',
    r'Copy \d+',
    r'Original',
    r'Duplicate',
    r'COPY',
    r'ORIGINAL'
]

# ============================================================================
# DOCUMENT CATEGORIES AND CLASSIFICATIONS
# ============================================================================

DOCUMENT_CATEGORIES = {
    'identity': [
        'passport', 'national_id', 'drivers_license', 'residence_permit',
        'citizenship_card', 'voter_id', 'aadhaar_card', 'pan_card',
        'social_security_card', 'health_insurance_card', 'student_id',
        'employee_id', 'military_id', 'government_id', 'immigration_document',
        'alien_registration_card', 'refugee_id', 'temporary_resident_card',
        'work_permit', 'visa_document', 'border_crossing_card', 'travel_document',
        'diplomatic_id', 'consular_id', 'maritime_id', 'aviation_id',
        'professional_license', 'occupational_license', 'medical_license',
        'law_license', 'teaching_license', 'engineering_license'
    ],
    'legal': [
        'contract', 'agreement', 'deed', 'power_of_attorney',
        'court_order', 'legal_notice', 'affidavit', 'will',
        'trust_document', 'lease_agreement', 'employment_contract',
        'non_disclosure_agreement', 'partnership_agreement'
    ],
    'financial': [
        'bank_statement', 'tax_return', 'invoice', 'receipt',
        'credit_card_statement', 'loan_document', 'insurance_policy',
        'financial_statement', 'audit_report', 'investment_document',
        'mortgage_document', 'credit_report'
    ],
    'educational': [
        'degree_certificate', 'diploma', 'transcript', 'report_card',
        'scholarship_document', 'academic_certificate', 'enrollment_certificate',
        'graduation_certificate', 'course_completion_certificate'
    ],
    'medical': [
        'medical_report', 'prescription', 'health_insurance',
        'vaccination_record', 'medical_certificate', 'lab_report',
        'discharge_summary', 'medical_history', 'treatment_plan'
    ],
    'business': [
        'business_license', 'incorporation_document', 'tax_registration',
        'commercial_invoice', 'shipping_document', 'purchase_order',
        'quotation', 'business_registration', 'trade_license'
    ],
    'other': []
}

# ============================================================================
# DOCUMENT FIELD TEMPLATES
# ============================================================================

DOCUMENT_FIELD_TEMPLATES = {
    "aadhaar_card": {
        "required_fields": ["aadhaar_number", "name", "date_of_birth", "gender", "address"],
        "optional_fields": ["father_name", "photo", "qr_code"],
        "field_patterns": {
            "aadhaar_number": r'\b\d{4}\s*\d{4}\s*\d{4}\b',
            "date_of_birth": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            "gender": r'\b(Male|Female|M|F)\b'
        }
    },
    "pan_card": {
        "required_fields": ["pan_number", "name", "father_name", "date_of_birth"],
        "optional_fields": ["photo", "signature"],
        "field_patterns": {
            "pan_number": r'\b[A-Z]{5}\d{4}[A-Z]\b',
            "date_of_birth": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
        }
    },
    "license": {
        "required_fields": ["license_number", "name", "date_of_birth", "address", "valid_from", "valid_until"],
        "optional_fields": ["vehicle_class", "issuing_authority", "photo"],
        "field_patterns": {
            "license_number": r'\b[A-Z]{2}\d{2}\s*\d{11}\b',
            "date_of_birth": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            "valid_from": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            "valid_until": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
        }
    },
    "passport": {
        "required_fields": ["passport_number", "surname", "given_names", "nationality", "date_of_birth", "place_of_birth"],
        "optional_fields": ["date_of_issue", "date_of_expiry", "issuing_authority", "photo"],
        "field_patterns": {
            "passport_number": r'\b[A-Z]\d{7}\b',
            "date_of_birth": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            "date_of_issue": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            "date_of_expiry": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'
        }
    },
    "resume": {
        "required_fields": ["name", "contact_information"],
        "optional_fields": ["email", "phone", "address", "linkedin", "portfolio", "summary", "experience", "education", "skills", "certifications", "projects", "achievements"],
        "field_patterns": {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b[\+]?[1-9][\d\s\-\(\)]{7,15}\b',
            "linkedin": r'linkedin\.com/in/[\w\-]+',
            "portfolio": r'(behance\.net|dribbble\.com|github\.com)/[\w\-]+',
            "website": r'https?://[\w\-\.]+\.[a-z]{2,}'
        }
    },
    "cv": {
        "required_fields": ["name", "contact_information"],
        "optional_fields": ["email", "phone", "address", "linkedin", "portfolio", "summary", "experience", "education", "skills", "certifications", "projects", "achievements", "publications", "references"],
        "field_patterns": {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b[\+]?[1-9][\d\s\-\(\)]{7,15}\b',
            "linkedin": r'linkedin\.com/in/[\w\-]+',
            "portfolio": r'(behance\.net|dribbble\.com|github\.com)/[\w\-]+',
            "website": r'https?://[\w\-\.]+\.[a-z]{2,}'
        }
    }
}

# ============================================================================
# DOCUMENT INDICATORS AND KEYWORDS
# ============================================================================

DOCUMENT_INDICATORS = {
    "aadhaar_card": [
        "aadhaar", "aadhar", "uidai", "unique identification",
        "आधार", "यूआईडीएआई", "12-digit", "enrollment number"
    ],
    "pan_card": [
        "pan", "permanent account number", "income tax",
        "tax identification", "10-character", "alphanumeric"
    ],
    "license": [
        "driving license", "dl", "license number", "vehicle class",
        "rto", "dmv", "transport authority", "driving permit"
    ],
    "passport": [
        "passport", "travel document", "nationality", "immigration",
        "border control", "embassy", "consulate", "visa"
    ]
}

# Content Quality Indicators
CONTENT_INDICATORS = {
    "high_quality": [
        "clear text", "readable", "official format", "proper structure",
        "complete information", "valid dates", "consistent formatting"
    ],
    "low_quality": [
        "blurry", "unclear", "incomplete", "damaged", "poor scan",
        "missing information", "illegible", "corrupted"
    ]
}

# Non-genuine Document Indicators
NON_GENUINE_INDICATORS = [
    "photocopy", "duplicate", "sample", "specimen", "template",
    "watermark missing", "poor quality", "inconsistent fonts",
    "misaligned text", "color variations", "pixelated image"
]

# ============================================================================
# OCR AND ERROR HANDLING CONSTANTS
# ============================================================================

# OCR Error Patterns
OCR_ERROR_PATTERNS = [
    r'[^\w\s\.\,\-\(\)\[\]\{\}]',  # Unusual characters
    r'\b[a-zA-Z]{1}\b',            # Single characters
    r'\d{20,}',                    # Very long numbers
    r'[A-Z]{10,}',                 # Very long uppercase strings
    r'[a-z]{15,}'                  # Very long lowercase strings
]

# Character Patterns for Validation
CHARACTER_PATTERNS = {
    "alphanumeric": r'^[a-zA-Z0-9\s\-\.]+$',
    "numeric": r'^\d+$',
    "alphabetic": r'^[a-zA-Z\s]+$',
    "date": r'^\d{1,2}[/-]\d{1,2}[/-]\d{4}$',
    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "phone": r'^[\+]?[1-9][\d]{0,15}$'
}

# Error Messages
ERROR_MESSAGES = {
    "file_not_found": "File not found or inaccessible",
    "unsupported_format": "Unsupported file format",
    "processing_failed": "Document processing failed",
    "ocr_failed": "OCR text extraction failed",
    "api_error": "API request failed",
    "timeout_error": "Processing timeout exceeded",
    "invalid_document": "Invalid or corrupted document",
    "low_confidence": "Low confidence in extraction results"
}

# Status Codes
STATUS_CODES = {
    "success": "success",
    "error": "error",
    "warning": "warning",
    "rejected": "rejected",
    "pending": "pending",
    "processing": "processing",
    "completed": "completed",
    "failed": "failed"
}

# ============================================================================
# DIRECTORY AND PATH CONSTANTS
# ============================================================================

# Default Directories
DEFAULT_TEMPLATES_DIR = "D:\\imageextractor\\identites\\Templates"
TEMPLATES_DIR = DEFAULT_TEMPLATES_DIR  # Backward compatibility
DEFAULT_OUTPUT_DIR = "results"
DEFAULT_TEMP_DIR = "temp"
DEFAULT_LOGS_DIR = "logs"

# File Extensions by Category
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif', '.webp'}
DOCUMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.rtf'}
ALL_SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS

# ============================================================================
# LOGGING AND DEBUG CONSTANTS
# ============================================================================

# Log Levels
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# Debug Flags
DEBUG_FLAGS = {
    "save_intermediate_images": False,
    "verbose_logging": False,
    "save_extracted_text": False,
    "profile_performance": False
}


CLASSIFICATION_PROMPT = """
Analyze this document image and identify the type of document by extracting only the following specific keywords if they are present: "license," "Pancard," or "aadharcard." , "passport," . Return the result in the following JSON format:        {
            "document_type": "The type of document (e.g., 'Pancard', 'License', 'AadhaarCard', 'Passport' ,'SSN' ,'passport' etc.)",
            "confidence_score": "A score between 0 and 1 indicating confidence in classification",
            "document_features": ["List of key features identified that helped in classification"]
        }
        Be specific with the document type and ensure that the document is valid  and only classify if confident.
        """


AADHAR_CARD_EXTRACTION = """
        Extract the following fields from the Aadhaar card in JSON format:
        {
            "document_type": "AadhaarCard",
            "data": {
                "aadhaar_number": "",
                "name": "",
                "gender": "",
                "date_of_birth": "",
                "address": "",
                "postal_code": ""
            }
        }
        Ensure Aadhaar number is properly formatted and dates are in YYYY-MM-DD format.
        """
PAN_CARD_EXTRACTION = """
        Extract the following fields from the PAN card in JSON format:
        {
            "document_type": "PAN_Card",
            "data": {
                "pan_number": "",
                "name": "",
                "fathers_name": "",
                "date_of_birth": "",
                "issue_date": ""
            }
        }
        Ensure PAN number is in correct format (AAAPL1234C) and dates are in YYYY-MM-DD format.
        """
LICENSE_EXTRACTION = """
        Extract the following fields from the driving license in JSON format:
        {
            "document_type": "License",
            "data": {
                "license_number": "",
                "name": "",
                "date_of_birth": "",
                "address": "",
                "valid_from": "",
                "valid_until": "",
                "vehicle_categories": [],
                "issuing_authority": ""
            }
        }
        Ensure all dates are in YYYY-MM-DD format and text fields are properly cased.
        """

PASSPORT_EXTRACTION = """ 

 Extract the following fields from the Passport in JSON format:
{
    "document_type": "Passport",
    "data": {
        "passport_number": "",
        "surname": "",
        "given_names": "",
        "nationality": "",
        "date_of_birth": "",
        "place_of_birth": "",
        "gender": "",
        "date_of_issue": "",
        "date_of_expiry": "",
        "place_of_issue": "",
        "type": "",
        "country_code": ""
    }
}
- Passport number format:
    * For US passports: 9 alphanumeric characters (e.g., 123456789 or C12345678).
    * For other countries: May start with an uppercase letter, followed by 7–9 digits.
- Dates should be in ISO format (YYYY-MM-DD).
- Country code must be a valid 3-letter ISO country code (e.g., IND for India, USA for United States).
- Gender should be one of: M (Male), F (Female), or X (Unspecified).
- Type must be one of the following: 
    * P (Personal)
    * D (Diplomatic)
    * S (Service)
Ensure extracted data adheres to these standards.

"""

jsonData = {

       "jsonData":{
        "EntityType": {
            "id": 1,
            "entityShortName": "LLC",
            "entityFullDesc": "Limited Liability Company",
            "onlineFormFilingFlag": False
        },
        "State": {
            "id": 33,
            "stateShortName": "NC",
            "stateFullDesc": "North Carolina",
            "stateUrl": "https://www.sosnc.gov/",
            "filingWebsiteUsername": "redberyl",
            "filingWebsitePassword": "yD7?ddG0!$09",
            "strapiDisplayName": "North-Carolina",
            "countryMaster": {
                "id": 3,
                "countryShortName": "US",
                "countryFullDesc": "United States"
            }
        },
        "County": {
            "id": 2006,
            "countyCode": "Alleghany",
            "countyName": "Alleghany",
            "stateId": {
                "id": 33,
                "stateShortName": "NC",
                "stateFullDesc": "North Carolina",
                "stateUrl": "https://www.sosnc.gov/",
                "filingWebsiteUsername": "redberyl",
                "filingWebsitePassword": "yD7?ddG0!$09",
                "strapiDisplayName": "North-Carolina",
                "countryMaster": {
                    "id": 3,
                    "countryShortName": "US",
                    "countryFullDesc": "United States"
                }
            }
        },
        "Payload": {
            "Entity_Formation": {
                "Name": {
                    "CD_LLC_Name": "redberyl llc",
                    "CD_Alternate_LLC_Name": "redberyl llc"
                },

                "Principal_Address": {
                    "PA_Address_Line_1": "123 Main Street",
                    "PA_Address_Line_2": "",
                    "PA_City": "Solapur",
                    "PA_Zip_Code": "11557",
                    "PA_State": "AL"
                },
                "Registered_Agent": {
                    "RA_Name": "Interstate Agent Services LLC",
                    "RA_Email_Address": "agentservice@vstatefilings.com",
                    "RA_Contact_No": "(718) 569-2703",
                    "Address": {
                        "RA_Address_Line_1": "6047 Tyvola Glen Circle, Suite 100",
                        "RA_Address_Line_2": "",
                        "RA_City": "Charlotte",
                        "RA_Zip_Code": "28217",
                        "RA_State": "NC"
                    }
                },
                "Billing_Information": {
                    "BI_Name": "Johson Charles",
                    "BI_Email_Address": "johson.charles@redberyktech.com",
                    "BI_Contact_No": "(555) 783-9499",
                    "BI_Address_Line_1": "123 Main Street",
                    "BI_Address_Line_2": "",
                    "BI_City": "Albany",
                    "BI_Zip_Code": "68342",
                    "BI_State": "AL"
                },
                "Mailing_Information": {
                    "MI_Name": "Johson Charles",
                    "MI_Email_Address": "johson.charles@redberyktech.com",
                    "MI_Contact_No": "(555) 783-9499",
                    "MI_Address_Line_1": "123 Main Street",
                    "MI_Address_Line_2": "",
                    "MI_City": "Albany",
                    "MI_Zip_Code": "68342",
                    "MI_State": "AL"
                },
                "Organizer_Information": {
                    "Organizer_Details": {
                        "Org_Name": "Johson Charles",
                        "Org_Email_Address": "johson.charles@redberyktech.com",
                        "Org_Contact_No": "(555) 783-9499"
                    },
                    "Address": {
                        "Org_Address_Line_1": "123 Main Street",
                        "Org_Address_Line_2": "",
                        "Org_City": "Albany",
                        "Org_Zip_Code": "68342",
                        "Org_State": "AL"
                    }
                }
            }
        }
       }

}
AUTOMATION_TASK= f"""
      ### **Advanced AI Agent for Automated LLC Registration** 
      
      For image buttons, try these approaches in order:

if their is button  with the name "Start Filing" or any relevant field then perform image click .
  Parent elements containing target text: //a[contains(., 'Start Filing')] | //button[contains(., 'Start Filing')]
       
      In case of 400 error reload the page and continue the automation from the point left  
      -Interact with the elements even though they are images not proper input fields.
      
      You are an advanced AI agent responsible for automating LLC registration form submissions across different state websites. Your task is to dynamically detect form fields, input the required data accurately, handle pop-ups or alerts, and ensure successful form submission. The AI should adapt to varying form structures and selectors without relying on predefined element locators.  
       If their are questions asked on the site like Has this entity been created in another state or country? or similar then select No from the dropdown 
       -Properly select all the fields and ensure that the fields are populated accurately
       - Properly Select the LLC entity type: `${jsonData["jsonData"]["EntityType"]["entityShortName"]}` or .`${jsonData["jsonData"]["EntityType"]["entityFullDesc"]}` from the dropdown or from any relevent field. 

       -Select the button with text Start Filing or Begin Filing or Start Register Business even if its an image ]
      ### **Task Execution Steps**  

      #### **1. Navigate to the Registration Page**  
    - Go to the url `${jsonData["jsonData"]["State"]["stateUrl"]}` url.  
    - Wait for the page to load completely.  

    #### **2. Handle Pop-ups and Initial UI Elements**  
    - Automatically close any pop-ups, notifications, or modals.  
    - Detect and handle Cloudflare captcha if present.  
    - Identify any initial login-related triggers:  
         - "Sign In" or "Login" buttons/links that open login forms  
    - Menu items or navigation elements that lead to login  
    - Modal triggers or popups for login  

#### **3. Perform Login (If Required)**  
- If a login form appears, identify:  
  - Username/email input field  
  - Password input field  
  - Login/Submit button  
- Enter credentials from the JSON:  
  - Username: `${jsonData["jsonData"]["State"]["filingWebsiteUsername"]}`  
  - Password: `${jsonData["jsonData"]["State"]["filingWebsitePassword"]}`  
- Click the login button and wait for authentication to complete.  

#### **4. Start LLC Registration Process**  
- Identify and click the appropriate link or button to start a new business  filing or Register  New Business button .
 
 -
- Select the LLC entity type: `${jsonData["jsonData"]["EntityType"]["entityShortName"]}` or .`${jsonData["jsonData"]["EntityType"]["entityFullDesc"]}` from the dropdown or from any relevent field. 
 - if the site ask for the options file online or upload the pdf select or click the file online button or select it from dropdown or from checkbox 
 -If a button has text like "Start Filing", "Begin Filing", or "Start Register Business", click it whether it's a standard button or an image.
 -If we need to save the name then click the save the name button or proceed next button.
- Proceed to the form.  

#### **5. Identify and Fill Required Fields**  
- Dynamically detect all required fields on the form and fill in the values from `${jsonData["jsonData"]["Payload"] }` make sure to flatten it at is dynamic json.  
- Ignore non-mandatory fields unless explicitly required for submission.  

#### **6. LLC Name and Designator**  
- Extract the LLC name from `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Name"]["CD_LLC_Name"]}`.  
- If  LLC a name does not work then replace the LLC name with the Alternate llc name  , use `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Name"]["CD_Alternate_LLC_Name"]}`.  
- Identify and select the appropriate business designator.  
- Enter the LLC name and ensure compliance with form requirements.  

#### **7. Registered Agent Information**  
- If an email field is detected, enter `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["RA_Email_Address"]}`. 

- Identify and respond to any required business declarations (e.g., tobacco-related questions, management type).  

#### **8. Principal Office Address** (If Required)  
- Detect address fields and input the values accordingly:  
  - Street Address: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_Address_Line_1"]}`.  
  - City: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_City"]}`.  
  - State: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_State"]}`.  
  - ZIP Code: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_Zip_Code"]}`.  

#### **9. Organizer Information** (If Required)  
- If the form includes an organizer section, enter `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Organizer_Information"]["Organizer_Details"]["Org_Name"]}`.  

#### **10. Registered Agent Details**  
-Enter the Registered Agent details in its respective fields only by identifying the label for Registered Agent
- Detect and select if the registered agent is an individual or business entity.  
- If required, extract and split the registered agent's full name   "from `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["RA_Name"]}`, then input:  
  - First Name  
  - Last Name  
  -If for example the name of the registered agent is Interstate Agent Services LLC then the  First Name would be "Interstate" and the Last Name would be "Agent Services LLC"
- If an address field is present, enter:  
  - Street Address/ Address Line_1 `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["Address"]["RA_Address_Line_1"]}`.  
  - City: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["Address"]["RA_City"]}`.  
  - ZIP Code or Zip Code or similar field: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["Address"]["RA_Zip_Code"]}`.  
  - IF  in the address their is requirement of County , select `${jsonData['jsonData']['County']['countyName']} either from dropdown or enter the value in it 

#### **11. Registered Agent Signature (If Required)**  
- If a signature field exists, input the registered agent's first and last name.  

#### **12. Finalization and Submission**  
- Identify and check any agreement or confirmation checkboxes.  
- Click the final submission button to complete the filing.  

#### **13. Handling Pop-ups, Alerts, and Dialogs**  
- Detect and handle any pop-ups, alerts, or confirmation dialogs.  
- If an alert appears, acknowledge and dismiss it before proceeding.  

#### **14. Response and Error Handling**  
- Return `"Form filled successfully"` upon successful completion.  
- If an error occurs, log it and return `"Form submission failed: <error message>"`.  
- If required fields are missing or contain errors, capture the issue and provide feedback on what needs to be corrected.  

### **AI Agent Execution Guidelines**  
- Dynamically detect and interact with form elements without relying on predefined selectors.  
- Adapt to different form structures and ignore unnecessary fields.  
- Handle UI changes and errors efficiently, ensuring smooth automation.  
- Maintain accuracy and compliance while minimizing user intervention.  

    
"""
MIN_CONFIDENCE_THRESHOLD=0.6
DOCUMENT_CATEGORIES = {
    'identity': [
        'passport', 'national_id', 'drivers_license', 'residence_permit',
        'citizenship_card', 'voter_id', 'aadhaar_card', 'pan_card',
        'social_security_card', 'health_insurance_card', 'student_id',
        'employee_id', 'military_id', 'government_id', 'immigration_document',
        'alien_registration_card', 'refugee_id', 'temporary_resident_card',
        'work_permit', 'visa_document', 'border_crossing_card', 'travel_document',
        'diplomatic_id', 'consular_id', 'maritime_id', 'aviation_id',
        'professional_license', 'occupational_license', 'medical_license',
        'law_license', 'teaching_license', 'engineering_license'
    ],
    'legal': [
        'contract', 'agreement', 'deed', 'power_of_attorney',
        'court_order', 'legal_notice', 'affidavit', 'will',
        'trust_deed', 'marriage_certificate', 'divorce_decree',
        'adoption_papers', 'custody_document', 'legal_opinion',
        'regulatory_compliance', 'intellectual_property_document',
        'patent_document', 'trademark_registration', 'copyright_document',
        'legal_brief', 'court_filing', 'legal_memorandum', 'legal_contract',
        'settlement_agreement', 'arbitration_award', 'legal_judgment',
        'legal_injunction', 'legal_subpoena', 'legal_warrant',
        'legal_pleading', 'legal_motion', 'legal_appeal', 'legal_brief',
        'legal_opinion', 'legal_advice', 'legal_consultation'
    ],
    'financial': [
        'bank_statement', 'tax_return', 'invoice', 'receipt',
        'credit_card_statement', 'loan_document', 'insurance_policy',
        'investment_statement', 'mortgage_document', 'payroll_document',
        'financial_report', 'budget_document', 'expense_report',
        'financial_audit', 'accounting_document', 'balance_sheet',
        'income_statement', 'cash_flow_statement', 'financial_forecast',
        'financial_plan', 'investment_proposal', 'financial_analysis',
        'financial_review', 'financial_summary', 'financial_statement',
        'financial_record', 'financial_transaction', 'financial_receipt',
        'financial_invoice', 'financial_contract', 'financial_agreement',
        'financial_certificate', 'financial_license', 'financial_permit'
    ],
    'educational': [
        'degree_certificate', 'diploma', 'transcript', 'report_card',
        'scholarship_document', 'academic_certificate', 'enrollment_document',
        'course_completion', 'professional_certification', 'training_certificate',
        'academic_transcript', 'student_record', 'educational_assessment',
        'academic_reference', 'educational_plan', 'academic_achievement',
        'academic_award', 'academic_merit', 'academic_honor',
        'academic_qualification', 'academic_credential', 'academic_license',
        'academic_permit', 'academic_certification', 'academic_verification',
        'academic_validation', 'academic_confirmation', 'academic_approval',
        'academic_authorization', 'academic_clearance', 'academic_eligibility'
    ],
    'medical': [
        'medical_report', 'prescription', 'health_insurance',
        'vaccination_record', 'medical_certificate', 'patient_record',
        'medical_history', 'diagnostic_report', 'treatment_plan',
        'medical_referral', 'discharge_summary', 'medical_bill',
        'medical_authorization', 'medical_consent', 'medical_imaging',
        'medical_scan', 'medical_test', 'medical_lab_result',
        'medical_analysis', 'medical_evaluation', 'medical_assessment',
        'medical_diagnosis', 'medical_prognosis', 'medical_recommendation',
        'medical_advice', 'medical_consultation', 'medical_opinion',
        'medical_verification', 'medical_validation', 'medical_confirmation',
        'medical_approval', 'medical_authorization', 'medical_clearance'
    ],
    'business': [
        'business_license', 'incorporation_document', 'tax_registration',
        'commercial_invoice', 'shipping_document', 'business_plan',
        'company_policy', 'employee_handbook', 'business_contract',
        'partnership_agreement', 'board_resolution', 'annual_report',
        'business_proposal', 'marketing_document', 'business_correspondence',
        'business_agreement', 'business_certificate', 'business_license',
        'business_permit', 'business_registration', 'business_incorporation',
        'business_formation', 'business_dissolution', 'business_merger',
        'business_acquisition', 'business_sale', 'business_purchase',
        'business_transfer', 'business_assignment', 'business_delegation',
        'business_authorization', 'business_approval', 'business_clearance'
    ],
    'government': [
        'government_id', 'permit', 'license', 'registration',
        'certificate', 'official_letter', 'government_form',
        'regulatory_document', 'compliance_certificate', 'government_report',
        'official_notice', 'government_contract', 'public_record',
        'government_authorization', 'official_documentation', 'government_approval',
        'government_clearance', 'government_verification', 'government_validation',
        'government_confirmation', 'government_certification', 'government_license',
        'government_permit', 'government_registration', 'government_incorporation',
        'government_formation', 'government_dissolution', 'government_merger',
        'government_acquisition', 'government_sale', 'government_purchase',
        'government_transfer', 'government_assignment', 'government_delegation'
    ],
    'employment': [
        'employment_contract', 'payslip', 'tax_form',
        'employment_certificate', 'resume', 'job_application',
        'performance_review', 'employment_verification', 'work_permit',
        'employee_benefits', 'termination_document', 'promotion_letter',
        'employment_agreement', 'job_description', 'employment_record',
        'employment_authorization', 'employment_approval', 'employment_clearance',
        'employment_verification', 'employment_validation', 'employment_confirmation',
        'employment_certification', 'employment_license', 'employment_permit',
        'employment_registration', 'employment_incorporation', 'employment_formation',
        'employment_dissolution', 'employment_merger', 'employment_acquisition',
        'employment_sale', 'employment_purchase', 'employment_transfer'
    ],
    'property': [
        'property_deed', 'mortgage_document', 'lease_agreement',
        'property_tax_document', 'survey_document', 'title_deed',
        'property_insurance', 'property_assessment', 'property_valuation',
        'property_inspection', 'property_maintenance', 'property_transfer',
        'property_development', 'property_management', 'property_contract',
        'property_authorization', 'property_approval', 'property_clearance',
        'property_verification', 'property_validation', 'property_confirmation',
        'property_certification', 'property_license', 'property_permit',
        'property_registration', 'property_incorporation', 'property_formation',
        'property_dissolution', 'property_merger', 'property_acquisition',
        'property_sale', 'property_purchase', 'property_transfer'
    ],
    'transportation': [
        'vehicle_registration', 'vehicle_title', 'vehicle_insurance',
        'vehicle_inspection', 'vehicle_maintenance', 'vehicle_transfer',
        'vehicle_authorization', 'vehicle_approval', 'vehicle_clearance',
        'vehicle_verification', 'vehicle_validation', 'vehicle_confirmation',
        'vehicle_certification', 'vehicle_license', 'vehicle_permit',
        'vehicle_registration', 'vehicle_incorporation', 'vehicle_formation',
        'vehicle_dissolution', 'vehicle_merger', 'vehicle_acquisition',
        'vehicle_sale', 'vehicle_purchase', 'vehicle_transfer',
        'vehicle_assignment', 'vehicle_delegation', 'vehicle_authorization',
        'vehicle_approval', 'vehicle_clearance', 'vehicle_verification'
    ],
    'insurance': [
        'insurance_policy', 'insurance_certificate', 'insurance_claim',
        'insurance_verification', 'insurance_validation', 'insurance_confirmation',
        'insurance_certification', 'insurance_license', 'insurance_permit',
        'insurance_registration', 'insurance_incorporation', 'insurance_formation',
        'insurance_dissolution', 'insurance_merger', 'insurance_acquisition',
        'insurance_sale', 'insurance_purchase', 'insurance_transfer',
        'insurance_assignment', 'insurance_delegation', 'insurance_authorization',
        'insurance_approval', 'insurance_clearance', 'insurance_verification',
        'insurance_validation', 'insurance_confirmation', 'insurance_certification',
        'insurance_license', 'insurance_permit', 'insurance_registration'
    ],
    'other': []  # For uncategorized document types
}


AUTOMATION_TASK1= f"""
# Advanced AI Agent for Automated LLC Registration

You are an AI agent tasked with automating LLC registration form submissions across state websites. Your primary responsibility is to accurately complete the registration process while handling various UI elements and form structures dynamically.

## Core Automation Rules

1. ALWAYS identify and interact with elements using multiple strategies:
   - Exact text matching
   - Partial text matching
   - ARIA labels
   - Placeholder text
   - Nearby label text
   - Image alt text
   - XPath containment

2. For any button labeled "Start Filing", "Begin Filing", or "Start Register Business":
   - First try: Direct button/link click
   - Second try: Parent element click
   - Third try: Use XPath: `//a[contains(., 'Start Filing')] | //button[contains(., 'Start Filing')]`
   - Fourth try: Image button click if element has image properties

3. On 400 errors:
   - Save current progress
   - Reload the page
   - Resume automation from last successful step
   - Retry the failed action up to 3 times

## Step-by-Step Execution Process

### 1. Initial Navigation
- Navigate to: `${jsonData["jsonData"]["State"]["stateUrl"]}`
- Wait for complete page load
- Handle any Cloudflare protection or captchas
- Close any initial popups or notifications

### 2. Authentication (If Required)
- Check for login requirement
- If login form present, enter:
  - Username: `${jsonData["jsonData"]["State"]["filingWebsiteUsername"]}`
  - Password: `${jsonData["jsonData"]["State"]["filingWebsitePassword"]}`
- Click login/submit button
- Verify successful authentication

### 3. Entity Type Selection
- Look for "Register New Business" or similar buttons
- Select LLC entity type using EITHER:
  - `${jsonData["jsonData"]["EntityType"]["entityShortName"]}`
  - OR `${jsonData["jsonData"]["EntityType"]["entityFullDesc"]}`
- If presented with "File Online" vs "Upload PDF" option, select "File Online"

### 4. LLC Name Entry
- Primary name: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Name"]["CD_LLC_Name"]}`
- If primary name fails, use: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Name"]["CD_Alternate_LLC_Name"]}`
- Click any "Save Name" or "Check Availability" buttons
- Handle any name validation responses

### 5. Common Questions
- For questions like "Has this entity been created in another state?" - Select "No"
- For general formation questions - Default to "No" unless specified otherwise
- Handle tobacco-related questions with "No"

### 6. Registered Agent Information
IMPORTANT: Only enter these in fields specifically labeled for Registered Agent
- Full Name: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["RA_Name"]}`
  - If name split required:
    - First Name: Use first word (e.g., "Interstate")
    - Last Name: Use remaining words (e.g., "Agent Services LLC")
- Email: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["RA_Email_Address"]}`
- Address:
  - Line 1: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["Address"]["RA_Address_Line_1"]}`
  - City: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["Address"]["RA_City"]}`
  - ZIP: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Registered_Agent"]["Address"]["RA_Zip_Code"]}`
  - County (if required): `${jsonData['jsonData']['County']['countyName']}`

### 7. Principal Office Address
When specifically requested:
- Address: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_Address_Line_1"]}`
- City: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_City"]}`
- State: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_State"]}`
- ZIP: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Principal_Address"]["PA_Zip_Code"]}`

### 8. Organizer Information
When required:
- Name: `${jsonData["jsonData"]["Payload"]["Entity_Formation"]["Organizer_Information"]["Organizer_Details"]["Org_Name"]}`

## Error Handling Requirements

1. Element Not Found:
   - Try all alternate selectors
   - Wait and retry up to 3 times
   - Log specific element that failed

2. Form Validation Errors:
   - Capture error message
   - Document field causing error
   - Try alternate data if available
   - Report specific failure reason

3. Page Timeout/Load Issues:
   - Implement wait and retry logic
   - Verify page state before proceeding
   - Resume from last known good state

## Success Criteria

Must verify ALL of these before completing:
1. All required fields are populated
2. No validation errors present
3. Form successfully submitted
4. Confirmation received
5. Any transaction ID captured

## Response Format

Return one of these specific messages:
- Success: "Form filled successfully"
- Failure: "Form submission failed: [specific error message]"

## Important Notes

1. NEVER skip validation steps
2. ALWAYS verify field labels before data entry
3. ALWAYS handle popup dialogs or alerts
4. ONLY fill fields that match exact section labels
5. MAINTAIN accurate progress tracking
6. VERIFY all data entry before submission
7. LOG all significant actions and errors
8. DO NOT proceed if critical fields are missing
"""





SSN_EXTRACTION = "Extract the following fields from the SSN document: ssn, name, date_of_birth, address."
