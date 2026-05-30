import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Linking,
  Platform,
  RefreshControl,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';
import Constants from 'expo-constants';
import * as Haptics from 'expo-haptics';
import * as SplashScreen from 'expo-splash-screen';
import * as Network from 'expo-network';

SplashScreen.preventAutoHideAsync().catch(() => {});

const APP_URL = Constants.expoConfig?.extra?.appUrl || 'https://progress-hub-256.emergent.host';
const SUPPORT_EMAIL = Constants.expoConfig?.extra?.supportEmail || 'support@anchorhelp.com.au';
const COLORS = {
  bg: '#F3EDE0',
  sage: '#586E58',
  terracotta: '#C26952',
  ink: '#2D332D',
  inkSoft: '#5C645C',
  white: '#FFFFFF',
};

// Region-aware crisis numbers (mirrors web app's crisis hotlines)
const CRISIS_NUMBERS = [
  { label: '988 (US)', tel: '988' },
  { label: '116 123 — Samaritans (UK/IE)', tel: '116123' },
  { label: '13 11 14 — Lifeline (AU)', tel: '131114' },
];

export default function App() {
  const webRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [networkError, setNetworkError] = useState(false);
  const [appReady, setAppReady] = useState(false);

  // Mark app ready -> dismiss native splash
  useEffect(() => {
    const t = setTimeout(() => {
      setAppReady(true);
      SplashScreen.hideAsync().catch(() => {});
    }, 350);
    return () => clearTimeout(t);
  }, []);

  // Check connectivity on mount
  useEffect(() => {
    Network.getNetworkStateAsync()
      .then((s) => setNetworkError(!s.isConnected || !s.isInternetReachable))
      .catch(() => setNetworkError(false));
  }, []);

  const onCrisisPress = useCallback(() => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium).catch(() => {});
    Alert.alert(
      'Need help right now?',
      'You are not alone. Tap a number below to call. These lines are free, confidential, and answered by trained people.',
      [
        ...CRISIS_NUMBERS.map((c) => ({
          text: c.label,
          onPress: () => Linking.openURL(`tel:${c.tel}`).catch(() => {}),
        })),
        { text: 'Close', style: 'cancel' },
      ],
      { cancelable: true }
    );
  }, []);

  const onRefresh = useCallback(() => {
    Haptics.selectionAsync().catch(() => {});
    setRefreshing(true);
    webRef.current?.reload();
    setTimeout(() => setRefreshing(false), 1200);
  }, []);

  const onShouldStartLoadWithRequest = useCallback((req) => {
    const u = req.url || '';
    // Handle native links (tel:, mailto:, external https that aren't our app)
    if (u.startsWith('tel:') || u.startsWith('mailto:') || u.startsWith('sms:')) {
      Linking.openURL(u).catch(() => {});
      return false;
    }
    // Allow all navigation inside our own domain + emergent preview
    const isOurApp =
      u.startsWith(APP_URL) ||
      u.startsWith('https://progress-hub-256.preview.emergentagent.com') ||
      u.startsWith('about:') ||
      u.startsWith('blob:') ||
      u.startsWith('data:');
    if (!isOurApp && u.startsWith('http')) {
      Linking.openURL(u).catch(() => {});
      return false;
    }
    return true;
  }, []);

  const retryNetwork = useCallback(async () => {
    Haptics.selectionAsync().catch(() => {});
    const s = await Network.getNetworkStateAsync().catch(() => ({ isConnected: true, isInternetReachable: true }));
    if (s.isConnected && s.isInternetReachable) {
      setNetworkError(false);
      webRef.current?.reload();
    } else {
      Alert.alert("Still offline", "Check your Wi-Fi or cellular data, then tap Retry.");
    }
  }, []);

  if (!appReady) {
    return (
      <SafeAreaProvider>
        <View style={styles.splashContainer}>
          <ActivityIndicator color={COLORS.sage} size="large" />
        </View>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />
      <SafeAreaView style={styles.container} edges={['top']}>
        {networkError ? (
          <ScrollView
            contentContainerStyle={styles.offlineWrap}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={COLORS.sage} />}
          >
            <Text style={styles.offlineEyebrow}>OFFLINE</Text>
            <Text style={styles.offlineTitle}>You're not connected.</Text>
            <Text style={styles.offlineBody}>
              Anchor needs an internet connection to load your private data. Your entries are kept safely on our server until you're back.
            </Text>
            <TouchableOpacity style={styles.retryBtn} onPress={retryNetwork} accessibilityRole="button">
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.crisisLink} onPress={onCrisisPress} accessibilityRole="button">
              <Text style={styles.crisisLinkText}>Need help now? Tap to call a crisis line</Text>
            </TouchableOpacity>
          </ScrollView>
        ) : (
          <>
            <WebView
              ref={webRef}
              source={{ uri: APP_URL }}
              style={styles.web}
              originWhitelist={['http://*', 'https://*', 'tel:*', 'mailto:*', 'blob:*', 'data:*']}
              onLoadStart={() => setLoading(true)}
              onLoadEnd={() => setLoading(false)}
              onError={() => setNetworkError(true)}
              onHttpError={(e) => {
                // 5xx from the server — show a soft retry, don't kill the session for 4xx (auth flows)
                const status = e?.nativeEvent?.statusCode;
                if (status && status >= 500) setNetworkError(true);
              }}
              startInLoadingState={false}
              allowsBackForwardNavigationGestures
              pullToRefreshEnabled
              decelerationRate="normal"
              javaScriptEnabled
              domStorageEnabled
              sharedCookiesEnabled
              thirdPartyCookiesEnabled
              allowsInlineMediaPlayback
              mediaPlaybackRequiresUserAction={false}
              onShouldStartLoadWithRequest={onShouldStartLoadWithRequest}
              setSupportMultipleWindows={false}
              applicationNameForUserAgent="AnchorRecoveryiOS/1.0"
              userAgent={
                Platform.OS === 'ios'
                  ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1 AnchorRecoveryiOS/1.0'
                  : undefined
              }
            />
            {loading && (
              <View pointerEvents="none" style={styles.loadingOverlay}>
                <ActivityIndicator color={COLORS.sage} />
              </View>
            )}

            <TouchableOpacity
              style={styles.crisisFab}
              onPress={onCrisisPress}
              accessibilityRole="button"
              accessibilityLabel="Need help now — opens crisis hotline options"
              activeOpacity={0.85}
            >
              <Text style={styles.crisisFabText}>Need help now?</Text>
            </TouchableOpacity>
          </>
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bg },
  splashContainer: { flex: 1, backgroundColor: COLORS.bg, alignItems: 'center', justifyContent: 'center' },
  web: { flex: 1, backgroundColor: COLORS.bg },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(243, 237, 224, 0.4)',
  },
  crisisFab: {
    position: 'absolute',
    right: 16,
    bottom: 28,
    backgroundColor: COLORS.terracotta,
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderRadius: 999,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 3 },
    elevation: 4,
  },
  crisisFabText: { color: COLORS.white, fontSize: 14, fontWeight: '600', letterSpacing: 0.2 },
  offlineWrap: { padding: 28, paddingTop: 64, alignItems: 'flex-start' },
  offlineEyebrow: { fontSize: 11, letterSpacing: 2, color: COLORS.terracotta, fontWeight: '600' },
  offlineTitle: { fontSize: 34, color: COLORS.ink, marginTop: 8, fontWeight: '300' },
  offlineBody: { marginTop: 14, fontSize: 15, color: COLORS.inkSoft, lineHeight: 22 },
  retryBtn: {
    marginTop: 28,
    backgroundColor: COLORS.sage,
    paddingHorizontal: 28,
    paddingVertical: 14,
    borderRadius: 999,
  },
  retryText: { color: COLORS.white, fontSize: 15, fontWeight: '600', letterSpacing: 0.3 },
  crisisLink: { marginTop: 28 },
  crisisLinkText: { color: COLORS.terracotta, fontSize: 14, textDecorationLine: 'underline' },
});
