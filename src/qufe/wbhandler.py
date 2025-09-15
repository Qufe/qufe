"""
Web Browser Automation Handler

This module provides enhanced browser automation capabilities using pure Selenium
with custom timeout configurations, network monitoring, tab management, and interactive element discovery.

Required dependencies:
    pip install qufe[web]

This installs: selenium>=4.0.0

Classes:
    Browser: Base class for browser automation with common functionality and tab management
    Chrome: Chrome browser implementation with advanced configuration options
    Firefox: Firefox browser implementation with profile management
"""

import os
import sys
import json
import time
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any, Optional, Union


# Lazy imports for external dependencies
def _import_selenium_dependencies():
    """Lazy import selenium with helpful error message."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.common.exceptions import (
            WebDriverException, TimeoutException, NoSuchElementException
        )

        return {
            'webdriver': webdriver,
            'By': By,
            'WebDriverWait': WebDriverWait,
            'EC': EC,
            'ActionChains': ActionChains,
            'ChromeOptions': ChromeOptions,
            'FirefoxOptions': FirefoxOptions,
            'FirefoxService': FirefoxService,
            'ChromeService': ChromeService,
            'WebDriverException': WebDriverException,
            'TimeoutException': TimeoutException,
            'NoSuchElementException': NoSuchElementException,
        }
    except ImportError as e:
        raise ImportError(
            "Web browser automation requires Selenium. "
            "Install with: pip install qufe[web]"
        ) from e


class TimeoutConfig:
    """Custom timeout configuration to replace SeleniumBase settings."""
    
    MINI_TIMEOUT = 5         # Default 2s → 5s
    SMALL_TIMEOUT = 20       # Default 7s → 20s
    LARGE_TIMEOUT = 40       # Default 10s → 40s
    EXTREME_TIMEOUT = 80     # Default 30s → 80s
    PAGE_LOAD_TIMEOUT = 180  # Default 120s → 180s


def help():
    """
    Display help information for web browser automation.

    Shows installation instructions, available classes, and usage examples.
    """
    print("qufe.wbhandler - Web Browser Automation")
    print("=" * 45)
    print()

    try:
        _import_selenium_dependencies()
        print("✓ Dependencies: INSTALLED")
    except ImportError:
        print("✗ Dependencies: MISSING")
        print("  Install with: pip install qufe[web]")
        print("  This installs: selenium>=4.0.0")
        print()
        return

    print()
    print("AVAILABLE CLASSES:")
    print("  • Browser: Base class for browser automation with tab management")
    print("  • Chrome: Chrome browser with advanced configuration options")
    print("  • Firefox: Firefox browser with profile management")
    print()

    print("FEATURES:")
    print("  • Pure Selenium with custom timeout configurations")
    print("  • Auto-detect selector types (XPath: //, CSS: $)")
    print("  • Network request monitoring via JavaScript injection")
    print("  • Tab management (open, switch, close)")
    print("  • Interactive element discovery and automation")
    print("  • URL parameter extraction and parsing")
    print("  • Cross-platform Firefox profile detection")
    print("  • Method chaining for Chrome configuration")
    print("  • Security-first design with optional insecure modes")
    print()

    print("SELECTOR SHORTCUTS:")
    print("  • XPath: '//button[text()=\"Submit\"]' (starts with //)")
    print("  • CSS: '$#my-id' or '$ .my-class' (starts with $)")
    print("  • Legacy: by='css' or by='xpath' (still supported)")
    print()

    print("TAB MANAGEMENT:")
    print("  • browser.open_new_tab('https://example.com')")
    print("  • browser.switch_to_tab(0)  # Switch to first tab")
    print("  • browser.get_tab_count()   # Get number of tabs")
    print("  • browser.close_current_tab()")
    print()

    print("SECURITY CONFIGURATION:")
    print("  • Default: Secure mode with standard security features enabled")
    print("  • Testing: Use configure_insecure_mode() for testing environments")
    print("  • Warning: Insecure mode disables important security features")
    print()

    print("USAGE EXAMPLE:")
    print("  from qufe.wbhandler import Chrome")
    print("  ")
    print("  # Start browser with method chaining (secure by default)")
    print("  browser = Chrome()")
    print("  browser.configure_no_automation().configure_detach()")
    print("  browser.open('https://example.com')")
    print("  ")
    print("  # For testing environments only")
    print("  browser.configure_insecure_mode()  # ⚠️ Use with caution")
    print("  ")
    print("  # Tab management")
    print("  browser.open_new_tab('https://github.com')")
    print("  browser.switch_to_tab(0)  # Back to first tab")
    print("  ")
    print("  # Auto-detect selectors")
    print("  browser.click('//button[text()=\"Login\"]')  # XPath")
    print("  browser.type_text('$#username', 'user')      # CSS ID")
    print("  browser.click('$ .submit-btn')               # CSS Class")
    print("  ")
    print("  # Clean up")
    print("  browser.quit()")
    print()

    print("NOTE: Requires WebDriver (ChromeDriver/GeckoDriver) to be installed")


class Browser:
    """
    Base browser automation class with enhanced functionality including tab management.

    Provides network monitoring, element discovery, tab management, and automation utilities
    built on top of pure Selenium WebDriver with auto-detecting selectors.

    Attributes:
        driver: Selenium WebDriver instance for browser automation
        wait: WebDriverWait instance for explicit waits
        window_handles: List of window handles for tab management
    """

    def __init__(
        self,
        private_mode: bool = True,
        mobile_mode: bool = False,
        headless: bool = False,
        window_size: str = "1920,1080",
        window_position: str = "10,10"
    ):
        """
        Initialize browser instance.

        Args:
            private_mode: Enable private/incognito browsing mode
            mobile_mode: Enable mobile device emulation
            headless: Run browser in headless mode
            window_size: Browser window size as "width,height"
            window_position: Browser window position as "x,y"

        Raises:
            ImportError: If required dependencies are not installed
        """
        # Import required dependencies
        self.selenium = _import_selenium_dependencies()

        self._private_mode = private_mode
        self._mobile_mode = mobile_mode
        self._headless = headless
        self._window_size = window_size
        self._window_position = window_position
        
        # Initialize driver and tab management
        self.driver = None
        self.wait = None
        self.window_handles = []
        self._init_webdriver()
        
        # Configure timeouts
        self._configure_timeouts()

    def _init_webdriver(self) -> None:
        """Initialize webdriver with specified configuration."""
        raise NotImplementedError("Subclasses must implement _init_webdriver method")

    def _configure_timeouts(self) -> None:
        """Configure browser timeouts."""
        if self.driver:
            self.driver.implicitly_wait(TimeoutConfig.MINI_TIMEOUT)
            self.driver.set_page_load_timeout(TimeoutConfig.PAGE_LOAD_TIMEOUT)
            self.wait = self.selenium['WebDriverWait'](self.driver, TimeoutConfig.SMALL_TIMEOUT)
            
            # Initialize window handles list
            try:
                self.window_handles = [self.driver.current_window_handle]
            except self.selenium['WebDriverException']:
                self.window_handles = []

    def _validate_driver(self) -> None:
        """Validate that driver is initialized. Fail-fast approach."""
        if self.driver is None:
            raise RuntimeError("Driver not initialized")

    def _parse_selector(self, selector: str, by: Optional[str] = None) -> tuple:
        """
        Parse selector and determine the appropriate By strategy.
        
        Auto-detects selector type based on SeleniumBase conventions:
        - Starts with '//' → XPath
        - Starts with '$' → CSS Selector
        - Otherwise → Use explicit 'by' parameter or default to CSS
        
        Args:
            selector: The selector string
            by: Explicit selector type ('css', 'xpath', or None for auto-detect)
            
        Returns:
            Tuple of (By strategy, cleaned selector)
            
        Raises:
            ValueError: If by parameter is invalid
        """
        if not selector:
            raise ValueError("Selector cannot be empty")
            
        # Auto-detect based on selector prefix
        if selector.startswith('//'):
            return (self.selenium['By'].XPATH, selector)
        elif selector.startswith('$'):
            # Remove $ prefix and handle space after $ for class selectors
            cleaned_selector = selector[1:].lstrip()
            return (self.selenium['By'].CSS_SELECTOR, cleaned_selector)
        
        # Fall back to explicit 'by' parameter
        if by is None:
            by = "css"  # Default to CSS
            
        if by.lower() == "css":
            return (self.selenium['By'].CSS_SELECTOR, selector)
        elif by.lower() == "xpath":
            return (self.selenium['By'].XPATH, selector)
        else:
            raise ValueError("by parameter must be 'css' or 'xpath'")

    def open(self, url: str) -> None:
        """
        Navigate to the specified URL.

        Args:
            url: URL to navigate to
        """
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        self.driver.get(url)

    def find_element(self, selector: str, by: Optional[str] = None):
        """
        Find a single element using auto-detected or explicit selector type.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)

        Returns:
            WebElement if found

        Raises:
            NoSuchElementException: If element not found
            ValueError: If selector is invalid
        """
        by_strategy, cleaned_selector = self._parse_selector(selector, by)
        return self.driver.find_element(by_strategy, cleaned_selector)

    def find_elements(self, selector: str, by: Optional[str] = None):
        """
        Find multiple elements using auto-detected or explicit selector type.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)

        Returns:
            List of WebElements
        """
        by_strategy, cleaned_selector = self._parse_selector(selector, by)
        return self.driver.find_elements(by_strategy, cleaned_selector)

    def wait_for_element(self, selector: str, by: Optional[str] = None, timeout: Optional[int] = None):
        """
        Wait for element to be present and visible.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)
            timeout: Custom timeout in seconds

        Returns:
            WebElement when found
        """
        wait_timeout = timeout or TimeoutConfig.SMALL_TIMEOUT
        wait = self.selenium['WebDriverWait'](self.driver, wait_timeout)
        
        by_strategy, cleaned_selector = self._parse_selector(selector, by)
        locator = (by_strategy, cleaned_selector)
            
        return wait.until(self.selenium['EC'].visibility_of_element_located(locator))

    def wait_for_ready_state_complete(self, timeout: Optional[int] = None) -> None:
        """
        Wait for page to reach ready state complete.

        Args:
            timeout: Maximum time to wait in seconds
        """
        wait_timeout = timeout or TimeoutConfig.SMALL_TIMEOUT
        wait = self.selenium['WebDriverWait'](self.driver, wait_timeout)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

    def wait_for_ajax(self, timeout: int = 20) -> None:
        """
        Wait for AJAX requests to complete.

        Args:
            timeout: Maximum time to wait in seconds
        """
        wait = self.selenium['WebDriverWait'](self.driver, timeout)
        wait.until(
            lambda drv: drv.execute_script(
                "return window.jQuery ? jQuery.active == 0 : true"
            )
        )

    def sleep(self, seconds: float) -> None:
        """
        Sleep for specified number of seconds.

        Args:
            seconds: Time to sleep
        """
        time.sleep(seconds)

    def click(self, selector: str, by: Optional[str] = None) -> None:
        """
        Click on element identified by selector.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            by: Explicit selection method ('css' or 'xpath', optional)
        """
        element = self.wait_for_element(selector, by)
        element.click()

    def type_text(self, selector: str, text: str, by: Optional[str] = None) -> None:
        """
        Type text into element identified by selector.

        Args:
            selector: Element selector (auto-detects XPath: //, CSS: $)
            text: Text to type
            by: Explicit selection method ('css' or 'xpath', optional)
        """
        element = self.wait_for_element(selector, by)
        element.clear()
        element.send_keys(text)

    def quit(self) -> None:
        """Clean up and quit the browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.window_handles.clear()

    # ==================== TAB MANAGEMENT ====================

    def get_current_handle(self) -> Optional[str]:
        """Get current window handle."""
        self._validate_driver()
        try:
            return self.driver.current_window_handle
        except self.selenium['WebDriverException']:
            return None

    def get_all_handles(self) -> List[str]:
        """Get all window handles."""
        self._validate_driver()
        try:
            return self.driver.window_handles
        except self.selenium['WebDriverException']:
            return []

    def switch_to_window(self, handle: str) -> bool:
        """
        Switch to window by handle.

        Args:
            handle: Window handle to switch to

        Returns:
            True if successful, False otherwise
        """
        self._validate_driver()
        try:
            self.driver.switch_to.window(handle)
            return True
        except self.selenium['WebDriverException']:
            return False

    def open_new_tab(self, url: Optional[str] = None) -> bool:
        """
        Open new tab and optionally navigate to URL.

        Args:
            url: Optional URL to open in new tab

        Returns:
            True if successful, False otherwise
        """
        self._validate_driver()
        try:
            self.driver.switch_to.new_window('tab')
            new_handle = self.driver.current_window_handle
            self.window_handles.append(new_handle)

            if url:
                self.driver.get(url)
            return True

        except self.selenium['WebDriverException']:
            return False

    def switch_to_tab(self, index: int = -1) -> bool:
        """
        Switch to tab by index.

        Args:
            index: Tab index (-1 for last tab)

        Returns:
            True if successful, False otherwise
        """
        self._validate_driver()
        try:
            # Refresh window handles list
            all_handles = self.get_all_handles()
            if all_handles:
                self.window_handles = all_handles

            if -len(self.window_handles) <= index < len(self.window_handles):
                target_handle = self.window_handles[index]
                return self.switch_to_window(target_handle)
            return False

        except (self.selenium['WebDriverException'], IndexError):
            return False

    def get_tab_count(self) -> int:
        """Get current number of tabs."""
        return len(self.get_all_handles())

    def close_current_tab(self) -> bool:
        """
        Close current tab and switch to previous tab.

        Returns:
            True if successful, False otherwise
        """
        self._validate_driver()
        try:
            if self.get_tab_count() <= 1:
                return False  # Don't close last tab

            current_handle = self.get_current_handle()
            self.driver.close()

            # Remove closed handle from our list
            if current_handle in self.window_handles:
                self.window_handles.remove(current_handle)

            # Switch to remaining tab
            remaining_handles = self.get_all_handles()
            if remaining_handles:
                return self.switch_to_window(remaining_handles[-1])
            return False

        except self.selenium['WebDriverException']:
            return False

    # ==================== NETWORK MONITORING ====================

    def inject_network_capture(self) -> None:
        """
        Inject JavaScript to capture fetch/XHR network requests.

        Creates a global __selenium_logs array that stores network request details
        including URL, status, method, request body, and response.
        """
        inject_script = """
        window.__selenium_logs = [];
        (function() {
          const origFetch = window.fetch;
          window.fetch = function(...args) {
            return origFetch(...args).then(res => {
              const clone = res.clone();
              clone.text().then(body => {
                window.__selenium_logs.push({
                  type: 'fetch', url: clone.url,
                  status: clone.status,
                  method: args[1]?.method||'GET',
                  request: args[1]?.body||null,
                  response: body
                });
              });
              return res;
            });
          };
          
          const _open = XMLHttpRequest.prototype.open;
          XMLHttpRequest.prototype.open = function(m,u) {
            this._m=m; this._u=u; return _open.apply(this, arguments);
          };
          
          const _send = XMLHttpRequest.prototype.send;
          XMLHttpRequest.prototype.send = function(b) {
            this.addEventListener('load', () => {
              window.__selenium_logs.push({
                type: 'xhr', url: this._u,
                status: this.status, method: this._m,
                request: b||null, response: this.responseText
              });
            });
            return _send.apply(this, arguments);
          };
        })();
        """

        self.driver.execute_script(inject_script)
        print('Network capture script injected successfully.')

    def get_network_logs(self) -> List[Dict[str, Any]]:
        """
        Retrieve captured network requests.

        Returns:
            List of network request dictionaries containing type, URL, status,
            method, request body, and response data.
        """
        # Ensure page is fully loaded before retrieving logs
        self.wait_for_ready_state_complete()
        self.wait_for_ajax()
        self.sleep(1)

        logs = self.driver.execute_script("return window.__selenium_logs;")
        return logs or []

    # ==================== UTILITY METHODS ====================

    @staticmethod
    def extract_url_parameters(
        url: str,
        param: str,
        split_char: str = ''
    ) -> List[List[str]]:
        """
        Extract parameter values from URL query string.

        Args:
            url: URL to parse
            param: Parameter name to extract ('get_all' returns all parameters)
            split_char: Character to split parameter values on

        Returns:
            List of parameter value lists
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        if param == 'get_all':
            return query_params

        parsed_params = query_params.get(param, [''])
        param_count = len(parsed_params)

        if param_count > 1:
            if split_char:
                return [value.split(split_char) for value in parsed_params]
            else:
                return [[value] for value in parsed_params]
        elif param_count == 1:
            value = parsed_params[0]
            return [value.split(split_char)] if split_char else [[value]]
        else:
            return []

    def find_element_info(self, selector: str, concat_text: bool = False) -> None:
        """
        Find and display information about elements matching the selector.

        Args:
            selector: CSS, XPath selector, or auto-detected (XPath: //, CSS: $)
            concat_text: If True, concatenate element text; if False, show detailed info
        """
        elements = self.find_elements(selector)

        if not elements:
            print(f'No elements found with selector: {selector}')
            return

        for element in elements:
            try:
                if not concat_text:
                    print(f'outerHTML: {element.get_attribute("outerHTML")}')
                    print(f'class: {element.get_attribute("class")}')
                    print(f'value: {element.get_attribute("value")}')
                    print(f'text: {element.text.strip()}', end='\n\n')
                else:
                    print(f"'{element.text.strip()}'", end=', ')
            except Exception:
                if not concat_text:
                    print("Error getting element info")
                else:
                    print("'[error]'", end=', ')

    @staticmethod
    def generate_text_selectors(
        texts: List[str],
        element_type: str,
    ) -> List[str]:
        """
        Generate XPath selectors for elements containing specific text.

        Args:
            texts: List of text content to match
            element_type: HTML element type (e.g., 'a', 'span', 'button')

        Returns:
            List of XPath selectors

        Example:
            generate_text_selectors(['Home', 'About'], 'a')
            # Returns: ["//a[normalize-space(.)='Home']", "//a[normalize-space(.)='About']"]
        """
        return [f"//{element_type}[normalize-space(.)='{text}']" for text in texts]

    def find_common_attribute(
        self,
        selectors: List[str],
        attribute: str,
        verbose: bool = False
    ) -> str:
        """
        Find the most common attribute value among elements matched by selectors.

        This method helps discover common patterns in element attributes,
        useful for building robust selectors when class names might change.

        Args:
            selectors: List of CSS, XPath, or auto-detected selectors
            attribute: Attribute name to analyze (e.g., 'class', 'id')
            verbose: Print detailed information if True

        Returns:
            Most frequently occurring attribute value

        Example:
            names = ['RaspberryPi', 'BlackBerry', 'Apple']
            selectors = [f"//label[normalize-space(text())='{name}']" for name in names]
            common_class = browser.find_common_attribute(selectors, 'class')
        """
        attribute_counts = {}

        for selector in selectors:
            elements = self.find_elements(selector)
            for element in elements:
                try:
                    attr_value = element.get_attribute(attribute)
                    if attr_value:
                        attribute_counts[attr_value] = attribute_counts.get(attr_value, 0) + 1
                except Exception:
                    continue

        if not attribute_counts:
            return ''

        most_common = max(attribute_counts, key=attribute_counts.get)

        if verbose:
            print(f'Most common {attribute}: {most_common}')
            print(f'Attribute distribution: {attribute_counts}')

        return most_common


class Chrome(Browser):
    """Chrome browser implementation with enhanced configuration options and method chaining."""

    def __init__(
        self,
        private_mode: bool = True,
        mobile_mode: bool = False,
        headless: bool = False,
        window_size: str = "1920,1080",
        window_position: str = "10,10"
    ):
        """
        Initialize Chrome browser with enhanced configuration.

        Args:
            private_mode: Enable private/incognito browsing mode
            mobile_mode: Enable mobile device emulation
            headless: Run browser in headless mode
            window_size: Browser window size as "width,height"
            window_position: Browser window position as "x,y"
        """
        # Initialize options before calling parent
        self.options = None
        super().__init__(private_mode, mobile_mode, headless, window_size, window_position)

    def _init_webdriver(self) -> None:
        """Initialize Chrome webdriver with custom options."""
        self.options = self.selenium['ChromeOptions']()
        self._setup_default_options()
        
        # Initialize driver
        try:
            self.driver = self.selenium['webdriver'].Chrome(options=self.options)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Chrome driver: {e}\n"
                "Make sure ChromeDriver is installed and in PATH"
            )

    def _setup_default_options(self) -> None:
        """Setup safe default Chrome options."""
        # Basic options
        if self._headless:
            self.options.add_argument('--headless')
        
        if self._private_mode:
            self.options.add_argument('--incognito')
        
        # Safe performance and stability options
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-plugins')
        self.options.add_argument('--disable-images')
        
        # Keep essential security features enabled by default
        # These are now moved to configure_insecure_mode() method
        
        # Mobile emulation
        if self._mobile_mode:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
            self.options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Window size and position
        if not self._mobile_mode:
            width, height = self._window_size.split(',')
            self.options.add_argument(f'--window-size={width},{height}')
            
            x, y = self._window_position.split(',')
            self.options.add_argument(f'--window-position={x},{y}')

    # ==================== METHOD CHAINING CONFIGURATION ====================

    def add_argument(self, argument: str) -> 'Chrome':
        """
        Add Chrome argument with method chaining.

        Args:
            argument: Chrome command line argument

        Returns:
            Self for method chaining
        """
        if self.options:
            self.options.add_argument(argument)
        return self

    def add_experimental_option(self, name: str, value: Any) -> 'Chrome':
        """
        Add Chrome experimental option.

        Args:
            name: Option name
            value: Option value

        Returns:
            Self for method chaining
        """
        if self.options:
            self.options.add_experimental_option(name, value)
        return self

    def configure_new_window(self) -> 'Chrome':
        """Configure Chrome to start with new window."""
        return self.add_argument('--new-window')

    def configure_proxy_pac(self, pac_url: str) -> 'Chrome':
        """
        Configure PAC-based proxy.

        Args:
            pac_url: PAC file URL
        """
        return self.add_argument(f'--proxy-pac-url={pac_url}')

    def configure_detach(self) -> 'Chrome':
        """Configure Chrome to stay open after script ends."""
        return self.add_experimental_option('detach', True)

    def configure_no_automation(self) -> 'Chrome':
        """Disable automation indicators."""
        return (self.add_experimental_option('excludeSwitches', ['enable-automation'])
                .add_experimental_option('useAutomationExtension', False))

    def configure_insecure_mode(self) -> 'Chrome':
        """
        Enable insecure options for testing environments only.
        
        ⚠️  WARNING: This disables important security features including:
        - Web security (Same-Origin Policy)
        - Sandbox protection
        - Mixed content blocking
        
        Only use this in controlled testing environments where you trust all content.
        Never use this for browsing untrusted websites or in production environments.
        
        Returns:
            Self for method chaining
        """
        print("⚠️  WARNING: Enabling insecure mode!")
        print("   This disables important Chrome security features.")
        print("   Only use in controlled testing environments.")
        print("   Features disabled:")
        print("   - Web security (Same-Origin Policy)")
        print("   - Sandbox protection") 
        print("   - Mixed content blocking")
        print()
        
        return (self.add_argument('--disable-web-security')
                .add_argument('--allow-running-insecure-content')
                .add_argument('--no-sandbox'))

    def configure_testing_mode(self) -> 'Chrome':
        """
        Configure Chrome for automated testing with minimal security restrictions.
        
        This is a safer alternative to configure_insecure_mode() that only disables
        sandbox for compatibility while keeping other security features.
        
        Returns:
            Self for method chaining
        """
        print("ℹ️  Configuring testing mode with minimal security impact...")
        return self.add_argument('--no-sandbox')


class Firefox(Browser):
    """Firefox browser implementation with profile management and private browsing."""

    def _init_webdriver(self) -> None:
        """
        Initialize Firefox webdriver with profile detection and private browsing.
        """
        options = self.selenium['FirefoxOptions']()
        
        # Basic options
        if self._headless:
            options.add_argument('--headless')
        
        # Profile configuration
        profile_path = self._find_firefox_profile()
        if profile_path:
            options.add_argument(f'-profile')
            options.add_argument(profile_path)
        
        # Private browsing
        if self._private_mode:
            options.add_argument('-private')
            options.set_preference('browser.privatebrowsing.autostart', True)
        
        # Safe performance preferences (keeping security features enabled)
        options.set_preference('network.proxy.type', 0)  # No proxy
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        
        # Mobile emulation for Firefox (basic user agent change)
        if self._mobile_mode:
            mobile_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            options.set_preference("general.useragent.override", mobile_user_agent)

        # Initialize driver
        try:
            self.driver = self.selenium['webdriver'].Firefox(options=options)
            
            # Set window size and position after initialization
            if not self._mobile_mode:
                width, height = map(int, self._window_size.split(','))
                x, y = map(int, self._window_position.split(','))
                
                self.driver.set_window_size(width, height)
                self.driver.set_window_position(x, y)
                
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Firefox driver: {e}\n"
                "Make sure GeckoDriver is installed and in PATH"
            )

    def configure_insecure_mode(self) -> 'Firefox':
        """
        Enable insecure options for testing environments only.
        
        ⚠️  WARNING: This disables important security features.
        Only use this in controlled testing environments where you trust all content.
        
        Returns:
            Self for method chaining
        """
        print("⚠️  WARNING: Enabling Firefox insecure mode!")
        print("   This disables important Firefox security features.")
        print("   Only use in controlled testing environments.")
        print()
        
        if self.driver:
            # Set insecure preferences via script execution
            self.driver.execute_script("""
                Components.utils.import("resource://gre/modules/Preferences.jsm");
                Preferences.set("security.tls.insecure_fallback_hosts", "*");
                Preferences.set("security.mixed_content.block_active_content", false);
            """)
        
        return self

    @staticmethod
    def _find_firefox_profile() -> Optional[str]:
        """
        Find Firefox default profile path across different operating systems.

        Returns:
            Path to Firefox profile directory or None if not found
        """
        try:
            if sys.platform == "darwin":  # macOS
                profile_dir = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/")
            elif sys.platform == "win32":  # Windows
                profile_dir = os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles/")
            else:  # Linux and other Unix-like systems
                profile_dir = os.path.expanduser("~/.mozilla/firefox/")

            if os.path.exists(profile_dir):
                profiles = [
                    d for d in os.listdir(profile_dir)
                    if d.endswith('.default-release')
                ]
                if profiles:
                    return os.path.join(profile_dir, profiles[0])
        except Exception:
            # Silently fail if profile detection fails
            pass
        return None


# Example usage demonstrating the enhanced functionality
if __name__ == '__main__':
    print("qufe.wbhandler Example Usage")
    print("=" * 30)
    
    # Example with Chrome and method chaining
    chrome = Chrome()
    
    try:
        print("Configuring Chrome with secure defaults...")
        chrome.configure_new_window().configure_no_automation().configure_detach()
        
        # Only enable insecure mode if absolutely necessary for testing
        print("\n🔒 Running in secure mode by default")
        print("   To enable insecure mode for testing, uncomment the next line:")
        print("   # chrome.configure_insecure_mode()")
        
        print("\nOpening first page...")
        chrome.open("https://httpbin.org/get")
        
        # Inject network capture
        chrome.inject_network_capture()
        print("✓ Network capture injected")
        
        # Demonstrate tab management
        print(f"Current tab count: {chrome.get_tab_count()}")
        
        print("Opening new tab...")
        if chrome.open_new_tab("https://httpbin.org/html"):
            print("✓ New tab opened")
            
        print(f"Updated tab count: {chrome.get_tab_count()}")
        
        # Switch between tabs
        print("Switching to first tab...")
        if chrome.switch_to_tab(0):
            print("✓ Switched to first tab")
            
        # Demonstrate URL parameter extraction
        test_url = "https://example.com?param1=value1&param2=value2,value3"
        params = Chrome.extract_url_parameters(test_url, 'param2', ',')
        print(f"Extracted params: {params}")
        
        print("Session completed successfully")
        
    except KeyboardInterrupt:
        print("\nSession interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up...")
        chrome.quit()
        print("Session ended")
