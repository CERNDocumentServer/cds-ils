export const config = {
  APP: {
    LOGO_SRC: null,
    HOME_SEARCH_BAR_PLACEHOLDER:
      "Search for books, e-books, series, journals and standards.",
    STATIC_PAGES: [
      { name: "about", route: "/about", apiURL: "1" },
      { name: "terms", route: "/terms", apiURL: "2" },
      { name: "faq", route: "/faq", apiURL: "3" },
      { name: "contact", route: "/contact", apiURL: "4" },
      { name: "search-guide", route: "/guide/search", apiURL: "5" },
      { name: "privacy-policy", route: "/privacy-policy", apiURL: "6" },
    ],
    ENABLE_LOCAL_ACCOUNT_LOGIN: false,
    ENABLE_SELF_CHECKOUT: true,
    OAUTH_PROVIDERS: {
      github: {
        enabled: false,
      },
      cern: {
        enabled: true,
        label: "Sign in with CERN",
        name: "cern",
        url: "/api/oauth/login/cern_openid/",
        icon: "",
        semanticUiColor: "grey",
        className: "",
      },
    },
    EMAILS_PREFILL: {
      subjectPrefix: "CERN Library:",
      footer:
        "\n\nKind regards,\nCERN Library\nLocation: building 52/1-052 on the Meyrin campus\nOpening hours:\n- Library is accessible 24/7.\n- Library desk (loans, returns, enquiries) and Bookshop: Monday - Friday, 8:30 a.m. - 6 p.m.\nEmail: library.desk@cern.ch",
    },
    ENVIRONMENTS: [
      {
        name: "dev",
        display: {
          text: "Development environment",
          color: "blue",
          icon: "code",
        },
      },
      {
        name: "sandbox",
        display: {
          text: "Sandbox environment",
          color: "teal",
          icon: "camera",
        },
      },
      {
        name: "production",
        display: {
          roles: ["admin"],
          text: "Production environment",
          color: "red",
          icon: "warning",
        },
      },
    ],
  },
  CIRCULATION: {
    extensionsMaxCount: 10000, // should be infinite
    requestStartOffset: 2,
    requestDuration: 120,
    loanWillExpireDays: 3,
  },
  VOCABULARIES: {
    documentRequests: {
      doc_req_type: "doc_req_type",
      doc_req_payment_method: "doc_req_payment_method",
      doc_req_medium: "doc_req_medium",
    },
    item: {
      identifier: {
        scheme: "item_identifier_scheme",
      },
    },
  },
  DOCUMENTS: {
    extensions: {
      label: "CERN",
      fields: {
        unit_accelerator: {
          label: "Accelerators",
          type: "string",
        },
        unit_experiment: {
          items: {
            label: "Experiment",
            type: "string",
          },
          label: "Experiments",
          type: "array",
        },
        unit_institution: {
          items: {
            label: "Institution",
            type: "string",
            widget: "vocabulary",
            vocabularyType: "document_institutions",
          },
          label: "Institutions",
          type: "array",
        },
        unit_project: {
          items: {
            label: "project",
            type: "string",
          },
          label: "Projects",
          type: "array",
        },
        unit_study: {
          items: {
            label: "Study",
            type: "string",
          },
          label: "Studies",
          type: "array",
        },
        standard_review_applicability: {
          items: {
            label: "Review applicability",
            type: "string",
            widget: "vocabulary",
            vocabularyType: "document_standard_reviews",
          },
          label: "Standard - Reviews applicability",
          type: "array",
        },
        standard_review_standard_validity: {
          label: "Standard - Review validity",
          type: "string",
        },
        standard_review_checkdate: {
          label: "Standard - Review check date",
          type: "date",
        },
        standard_review_comment: {
          label: "Standard - Review comment",
          type: "string",
        },
        standard_review_expert: {
          label: "Standard - Review expert",
          type: "string",
        },
      },
    },
    authors: {
      maxEditable: 30,
    },
  },
  ILL_BORROWING_REQUESTS: {
    defaultType: "PHYSICAL_COPY",
    fieldOverrides: {
      due_date: "Returned date",
    },
    search: {
      sort: [
        {
          order: 1,
          sortBy: "created",
          sortOrder: "desc",
          text: "Recently added",
        },
        {
          order: 2,
          sortBy: "bestmatch",
          sortOrder: "asc",
          text: "Most relevant",
        },
        {
          order: 3,
          sortBy: "request_date",
          sortOrder: "desc",
          text: "Request date",
        },
        {
          order: 4,
          sortBy: "expected_delivery_date",
          sortOrder: "desc",
          text: "Expected delivery date",
        },
        {
          order: 5,
          sortBy: "due_date",
          sortOrder: "desc",
          text: "Returned date",
        },
      ],
    },
  },
  PATRONS: {
    customFields: {
      personID: {
        field: "person_id",
      },
    },
    phonebookURLPrefix: "https://phonebook.cern.ch/search?q=",
  },
  ITEMS: {
    editorSchema: {
      required: [
        "internal_location_pid",
        "barcode",
        "status",
        "document_pid",
        "circulation_restriction",
        "medium",
        "identifiers",
      ],
    },
    editorUiSchema: {
      shelf: {
        "ui:widget": "vocabulary",
        "ui:options": {
          size: 125, // Make sure to update size when adding new shelfs
          vocabularyType: "shelf_number",
        },
      },
    },
    mediums: [
      {
        value: "NOT_SPECIFIED",
        text: "Not specified",
        label: "Not specified",
        order: 1,
      },
      { value: "PAPER", text: "Paper", label: "Paper", order: 2 },
      { value: "CDROM", text: "CD-ROM", label: "CD-ROM", order: 3 },
      { value: "DVD", text: "DVD", label: "DVD", order: 4 },
      { value: "VHS", text: "VHS", label: "VHS", order: 5 },
      {
        value: "PAPERBACK",
        text: "Paperback",
        label: "Paperback",
        order: 6,
      },
      {
        value: "HARDCOVER",
        text: "Hardcover",
        label: "Hardcover",
        order: 7,
      },
      { value: "AUDIO_CD", text: "Audio CD", label: "Audio CD", order: 8 },
    ],
  },
  IMPORTER: {
    providers: [
      { key: "springer", text: "Springer", value: "springer" },
      { key: "ebl", text: "EbookCentral (EBL)", value: "ebl" },
      { key: "safari", text: "O'reilly (Safari)", value: "safari" },
      { key: "snv", text: "SNV Standards", value: "snv" },
    ],
    modes: [
      { key: "create", text: "Import", value: "IMPORT" },
      { key: "delete", text: "Delete", value: "DELETE" },
    ],
    fetchTaskStatusIntervalSecs: 5000,
  },
  ACQ_ORDERS: {
    editorSchema: {
      definitions: {
        "order-line": {
          properties: {
            inter_departmental_transaction_id: {
              title: "ID of inter-departmental transaction (TID)",
              type: "string",
            },
          },
        },
        "payment": {
          properties: {
            internal_purchase_requisition_id: {
              title: "Internal purchase requisition ID (DAI)",
              type: "string",
            },
          },
        },
      },
    },
  },
};
