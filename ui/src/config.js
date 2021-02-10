export const config = {
  APP: {
    LOGO_SRC: null,
    STATIC_PAGES: [
      { name: 'about', route: '/about', apiURL: '1' },
      { name: 'terms', route: '/terms', apiURL: '2' },
      { name: 'faq', route: '/faq', apiURL: '3' },
      { name: 'contact', route: '/contact', apiURL: '4' },
      { name: 'search-guide', route: '/guide/search', apiURL: '5' },
    ],
    ENABLE_LOCAL_ACCOUNT_LOGIN: false,
    OAUTH_PROVIDERS: {
      github: {
        enabled: false,
      },
      cern: {
        enabled: true,
        label: 'Sign in with CERN',
        name: 'cern',
        url: '/api/oauth/login/cern_openid/',
        icon: '',
        semanticUiColor: 'grey',
        className: '',
      },
    },
    EMAILS_PREFILL: {
      subjectPrefix: 'CERN Library:',
      footer:
        '\n\nKind regards,\nCERN Library\nLocation: building 52/1-052 on the Meyrin campus\nOpening hours:\n- Library is accessible 24/7.\n- Library desk (loans, returns, enquiries) and Bookshop: Monday - Friday, 8:30 a.m. - 6 p.m.\nEmail: library.desk@cern.ch',
    },
    ENVIRONMENTS: [
      {
        name: 'dev',
        display: {
          text: 'Development environment',
          color: 'blue',
          icon: 'code',
        },
      },
      {
        name: 'sandbox',
        display: {
          text: 'Sandbox environment',
          color: 'teal',
          icon: 'camera',
        },
      },
      {
        name: 'production',
        display: {
          roles: ['admin'],
          text: 'Production environment',
          color: 'red',
          icon: 'warning',
        },
      },
    ],
  },
  CIRCULATION: {
    extensionsMaxCount: 10000, // should be infinite
    requestDuration: 120,
    loanWillExpireDays: 3,
  },
  VOCABULARIES: {
    documentRequests: {
      doc_req_type: 'doc_req_type',
      doc_req_payment_method: 'doc_req_payment_method',
      doc_req_medium: 'doc_req_medium',
    },
  },
  DOCUMENTS: {
    extensions: {
      label: 'Other',
      fields: {
        unit_accelerator: {
          label: 'Accelerator',
          type: 'vocabulary',
          vocabularyType: 'document_accelerators',
          default: '',
          line: 1,
        },
        unit_experiment: {
          label: 'Experiment',
          type: 'vocabulary',
          vocabularyType: 'document_experiments',
          default: '',
          line: 1,
        },
        unit_curated_relation: {
          label: 'Curated Relation',
          type: 'boolean',
          default: false,
          line: 1,
        },
        unit_institution: {
          label: 'Institution',
          type: 'vocabulary',
          vocabularyType: 'document_institutions',
          default: '',
          line: 2,
        },
        unit_project: {
          label: 'Project',
          type: 'string',
          default: '',
          line: 2,
        },
        unit_study: {
          label: 'Study',
          type: 'string',
          default: '',
          line: 2,
        },
        standard_review_applicability: {
          label: 'Status CERN Applicability',
          type: 'vocabulary',
          vocabularyType: 'document_standard_reviews',
          default: '',
          line: 3,
        },
        standard_review_standard_validity: {
          label: 'Status Standard Validity',
          type: 'string',
          default: '',
          isRequired: true,
          line: 3,
        },
        standard_review_checkdate: {
          label: 'Status check date',
          type: 'date',
          default: '',
          line: 3,
        },
        standard_review_comment: {
          label: 'Status comment',
          type: 'string',
          default: '',
          line: 4,
        },
        standard_review_expert: {
          label: 'Status expert',
          type: 'string',
          default: '',
          line: 4,
        },
      },
    },
  },
  PATRONS: {
    customFields: {
      personID: {
        field: 'person_id',
      },
    },
  },
  IMPORTER: {
    providers: [
      { key: 'springer', text: 'Springer', value: 'springer' },
      { key: 'ebl', text: 'EBL', value: 'ebl' },
      { key: 'safari', text: 'Safari', value: 'safari' },
    ],
    modes: [
      { key: 'create', text: 'Create', value: 'create' },
      { key: 'delete', text: 'Delete', value: 'delete' },
    ],
    fetchTaskStatusIntervalSecs: 5000,
  },
};
