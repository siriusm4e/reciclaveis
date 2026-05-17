import type { CapacitorConfig } from '@capacitor/cli';

/**
 * Capacitor — Plataforma Nacional de Resíduos
 *
 * - appId / appName: identidade nativa do app (App Store / Play Store)
 * - webDir: output do `vite build` que vira o bundle WebView
 * - server.androidScheme=https: Android só aceita storage local sob https
 * - server.url (comentado): habilita live-reload apontando para o IP do host
 *   na rede local durante desenvolvimento mobile. Deixar desligado em produção.
 *
 * Plugins habilitados:
 *   - @capacitor/push-notifications (FCM Android / APNs iOS)
 *   - @capacitor/geolocation (com fallback browser API via useCapacitor)
 */
const config: CapacitorConfig = {
  appId: 'com.pnr.app',
  appName: 'PNR',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    // url: 'http://192.168.0.10:5173', // descomentar para live-reload mobile
    // cleartext: true,
  },
  ios: {
    contentInset: 'always',
  },
  android: {
    allowMixedContent: false,
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    Geolocation: {
      // Plugin nativo lê do AndroidManifest.xml e Info.plist; aqui só placeholder
    },
  },
};

export default config;
