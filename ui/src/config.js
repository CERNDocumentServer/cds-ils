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
      label: 'CERN',
      fields: {
        unit_accelerator: {
          label: 'Accelerators',
          type: 'string',
        },
        unit_experiment: {
          items: {
            label: 'Experiment',
            type: 'string',
          },
          label: 'Experiments',
          type: 'array',
        },
        unit_institution: {
          items: {
            label: 'Institution',
            type: 'string',
            widget: 'vocabulary',
            vocabularyType: 'document_institutions',
          },
          label: 'Institutions',
          type: 'array',
        },
        unit_project: {
          label: 'Project',
          type: 'string',
        },
        unit_study: {
          items: {
            label: 'Study',
            type: 'string',
          },
          label: 'Studies',
          type: 'array',
        },
        standard_review_applicability: {
          items: {
            label: 'Review applicability',
            type: 'string',
            widget: 'vocabulary',
            vocabularyType: 'document_standard_reviews',
          },
          label: 'Standard - Reviews applicability',
          type: 'array',
        },
        standard_review_standard_validity: {
          label: 'Standard - Review validity',
          type: 'string',
        },
        standard_review_checkdate: {
          label: 'Standard - Review check date',
          type: 'date',
        },
        standard_review_comment: {
          label: 'Standard - Review comment',
          type: 'string',
        },
        standard_review_expert: {
          label: 'Standard - Review expert',
          type: 'string',
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
    phonebookURLPrefix: 'https://phonebook.cern.ch/search?q=',
  },
  ITEMS: {
    editorSchema: {
      required: [
        'internal_location_pid',
        'barcode',
        'shelf',
        'status',
        'document_pid',
        'circulation_restriction',
        'medium',
      ],
    },
  },
  IMPORTER: {
    providers: [
      { key: 'springer', text: 'Springer', value: 'springer' },
      { key: 'ebl', text: 'EBL', value: 'ebl' },
      { key: 'safari', text: 'Safari', value: 'safari' },
    ],
    modes: [
      { key: 'preview', text: 'Preview', value: 'PREVIEW' },
      { key: 'create', text: 'Create', value: 'CREATE' },
      { key: 'delete', text: 'Delete', value: 'DELETE' },
    ],
    fetchTaskStatusIntervalSecs: 5000,
  },
};
