# Инструкции по сборке приложений

## Windows приложение

### Установка зависимостей:
```bash
cd windows_app
pip install -r requirements.txt
pip install pyinstaller
```

### Сборка exe файла:
```bash
python build.py
```

Готовый файл будет в папке `dist/HarvestMessenger.exe`

### Альтернативный запуск:
```bash
python main.py
```

## iOS приложение

### Требования:
- macOS с Xcode
- Apple Developer Account (для публикации)

### Создание проекта:
1. Откройте Xcode
2. Create new project → iOS → App
3. Product Name: `Harvest Messenger`
4. Bundle Identifier: `com.harvest.messenger`
5. Language: Swift, Interface: SwiftUI

### Добавление файлов:
1. Замените `ContentView.swift` на файл из `ios_app/ContentView.swift`
2. Замените `HarvestMessengerApp.swift` на файл из `ios_app/HarvestMessengerApp.swift`
3. Замените `Info.plist` на файл из `ios_app/Info.plist`

### Сборка:
1. Product → Archive
2. Distribute App → App Store Connect

## Альтернативные решения

### Electron (кроссплатформенное):
```bash
npm init -y
npm install electron
```

### Flutter (кроссплатформенное):
```bash
flutter create harvest_messenger
```

### React Native:
```bash
npx react-native init HarvestMessenger
```