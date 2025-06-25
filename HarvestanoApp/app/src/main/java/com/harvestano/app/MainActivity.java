package com.harvestano.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.Toast;
import android.content.Intent;
import android.net.Uri;
import android.app.AlertDialog;
import android.content.DialogInterface;

public class MainActivity extends Activity {
    private WebView webView;
    private ProgressBar progressBar;
    private static final String ONION_URL = "http://harvestano.onion"; // Будет заменен на реальный адрес

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        progressBar = findViewById(R.id.progressBar);

        // Настройки WebView для Tor
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        webSettings.setSupportZoom(true);
        webSettings.setDefaultTextEncodingName("utf-8");
        
        // Дополнительные настройки для Tor
        webSettings.setAllowFileAccess(false);
        webSettings.setAllowContentAccess(false);
        webSettings.setAllowFileAccessFromFileURLs(false);
        webSettings.setAllowUniversalAccessFromFileURLs(false);
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        // Обработчик загрузки
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                progressBar.setVisibility(View.GONE);
                showTorErrorDialog();
            }
            
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                // Обрабатываем .onion ссылки
                if (url.contains(".onion")) {
                    view.loadUrl(url);
                    return true;
                }
                return false;
            }
        });

        // Проверяем доступность Tor
        checkTorAvailability();
    }

    private void checkTorAvailability() {
        // Показываем диалог с инструкциями по Tor
        new AlertDialog.Builder(this)
            .setTitle("🌐 Tor подключение")
            .setMessage("Для работы приложения необходимо:\n\n" +
                       "1. Установить Orbot (Tor для Android)\n" +
                       "2. Запустить Orbot и включить VPN\n" +
                       "3. Дождаться подключения к сети Tor\n\n" +
                       "Хотите установить Orbot сейчас?")
            .setPositiveButton("Установить Orbot", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    openOrbotPlayStore();
                }
            })
            .setNegativeButton("Продолжить", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    loadOnionSite();
                }
            })
            .setCancelable(false)
            .show();
    }

    private void openOrbotPlayStore() {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setData(Uri.parse("market://details?id=org.torproject.android"));
            startActivity(intent);
        } catch (Exception e) {
            // Если Play Store недоступен, открываем в браузере
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setData(Uri.parse("https://play.google.com/store/apps/details?id=org.torproject.android"));
            startActivity(intent);
        }
    }

    private void loadOnionSite() {
        // Загружаем .onion сайт
        // В реальном приложении здесь будет динамический адрес
        String onionAddress = getOnionAddress();
        webView.loadUrl("http://" + onionAddress);
    }

    private String getOnionAddress() {
        // В реальном приложении адрес может быть получен из конфигурации
        // или с сервера. Пока используем заглушку
        return "harvestano.onion";
    }

    private void showTorErrorDialog() {
        new AlertDialog.Builder(this)
            .setTitle("❌ Ошибка подключения")
            .setMessage("Не удалось подключиться к сайту через Tor.\n\n" +
                       "Возможные причины:\n" +
                       "• Orbot не запущен\n" +
                       "• VPN не включен\n" +
                       "• Проблемы с сетью Tor\n\n" +
                       "Проверьте настройки Orbot и попробуйте снова.")
            .setPositiveButton("Перезагрузить", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    loadOnionSite();
                }
            })
            .setNegativeButton("Настройки Orbot", new DialogInterface.OnClickListener() {
                @Override
                public void onClick(DialogInterface dialog, int which) {
                    openOrbotSettings();
                }
            })
            .setCancelable(false)
            .show();
    }

    private void openOrbotSettings() {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setData(Uri.parse("package:org.torproject.android"));
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(this, "Откройте настройки Orbot вручную", Toast.LENGTH_LONG).show();
        }
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
