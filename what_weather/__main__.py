from __future__ import annotations

from what_weather.app_factory import create_app

if __name__ == '__main__':
    app = create_app('development_config')
    app.run(host='0.0.0.0', port=5000)
