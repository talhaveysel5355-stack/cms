export default ({ env }) => ({
  // i18n is built into Strapi 5 core — no plugin needed
  // Default locale is configured via STRAPI_PLUGIN_I18N_INIT_LOCALE_CODE env var
  // Additional locales are added via Strapi Admin: Settings > Internationalization
  upload: {
    config: {
      provider: 'cloudinary',
      providerOptions: {
        cloud_name: env('CLOUDINARY_NAME'),
        api_key: env('CLOUDINARY_KEY'),
        api_secret: env('CLOUDINARY_SECRET'),
      },
      actionOptions: {
        upload: {},
        uploadStream: {},
        delete: {},
      },
    },
  },
});
