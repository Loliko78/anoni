# 📱 Push-уведомления для веб-приложения

## ✅ Что реализовано:

### 1. **Web Push API**
- Service Worker для обработки уведомлений
- Автоматический запрос разрешений
- Подписка на push-уведомления

### 2. **Backend интеграция**
- API `/api/push/subscribe` для регистрации подписок
- Отправка уведомлений при новых сообщениях в чатах и группах
- Сохранение подписок в базе данных

### 3. **Файлы добавлены:**
- `static/js/push-notifications.js` - клиентская логика
- `static/js/sw.js` - Service Worker
- `add_push_field.py` - миграция БД

## 🚀 Как работает:

1. **При первом посещении**: Автоматически запрашивается разрешение на уведомления
2. **При новом сообщении**: Отправляется push-уведомление получателю
3. **При клике на уведомление**: Открывается соответствующий чат

## 📱 Для Android WebView:

### В вашем Android приложении добавьте:

```java
// В WebViewClient
webView.getSettings().setJavaScriptEnabled(true);
webView.getSettings().setDomStorageEnabled(true);

// Разрешения в AndroidManifest.xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.VIBRATE" />
```

## 🔧 Настройка для продакшена:

1. **HTTPS обязательно** - push работает только через HTTPS
2. **Замените VAPID ключ** в `push-notifications.js` на свой
3. **Настройте Firebase** для полноценных push-уведомлений

## 🎯 Результат:

✅ Пользователи получают уведомления при новых сообщениях
✅ Работает в фоне даже когда приложение закрыто
✅ Поддержка Android WebView приложений
✅ Клик по уведомлению открывает нужный чат

**Готово к использованию!**