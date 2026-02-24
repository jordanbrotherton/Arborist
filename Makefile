APP_NAME = io.github.jordanbrotherton.arborist
APP_DIR = Arborist.AppDir
BUILD_DIR = builddir
AUX_DIR = build-aux
PYTHON_VERSION = 3.11

all: bundle

clean:
	rm -rf $(BUILD_DIR) $(APP_DIR)

install-meson:
	meson setup $(BUILD_DIR) --prefix=$(shell pwd)/$(APP_DIR)/usr
	meson install -C $(BUILD_DIR)

install-deps:
	pip install dbus-fast --target $(APP_DIR)/usr/lib/python3/site-packages/

apprun:
	ln -sf usr/share/applications/$(APP_NAME).desktop $(APP_DIR)/$(APP_NAME).desktop
	ln -sf usr/share/icons/hicolor/scalable/apps/$(APP_NAME).svg $(APP_DIR)/$(APP_NAME).svg
	@echo "Copying AppRun..."
	cp $(AUX_DIR)/AppRun $(APP_DIR)/AppRun
	chmod +x $(APP_DIR)/AppRun

bundle: install-meson install-deps apprun
	ARCH=x86_64 ./appimagetool-x86_64.AppImage $(APP_DIR) Arborist-x86_64.AppImage

