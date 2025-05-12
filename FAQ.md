# ChatUniTest Frequently Asked Questions (FAQ)

Here are some frequently asked questions about ChatUniTest.

1.  **Q: What is ChatUniTest?**
    **A:** ChatUniTest is a tool/framework designed to help developers generate unit tests for their Java code by leveraging Large Language Models (LLMs). It aims to streamline the test creation process and improve code coverage. The `chatunitest-core` library provides the core functionalities, and the `chatunitest-maven-plugin` allows easy integration into Maven build processes.

2.  **Q: How do I get started with ChatUniTest?**

    **A:** The primary way to get started is by configuring the `chatunitest-maven-plugin` （https://github.com/ZJU-ACES-ISE/chatunitest-maven-plugin）in your project's `pom.xml`. This plugin will utilize `chatunitest-core`.

    * **Configure Maven Plugin:** Add and configure the `chatunitest-maven-plugin` in your `pom.xml`. This includes setting up API keys, selecting models, and other necessary parameters. Please refer to our Maven Plugin Usage Guide for detailed configuration options and goals.
    * You'll need to configure access to an LLM (see next FAQ).

3.  **Q: How do I configure my API keys for Large Language Models (LLMs)?**
    **A:** ChatUniTest requires API keys to access LLMs for test generation. These keys should be configured within the `<configuration>` section of the `chatunitest-maven-plugin` in your `pom.xml`, specifically within an `<apiKeys>` tag.

    **Example:**
    ```xml
    <configuration>
        <apiKeys>
            <openaiKey>YOUR_OPENAI_API_KEY</openaiKey>
        </apiKeys>
    </configuration>
    ```
    Replace `YOUR_OPENAI_API_KEY` with your actual API key. Refer to the plugin documentation for specific key names if using different LLM providers.

4.  **Q: Which LLM models are currently supported, and can I add others?**
    **A:** ChatUniTest has built-in support for several models. As of the latest update, these include:
    * `gpt-3.5-turbo`
    * `gpt-3.5-turbo-1106`
    * `gpt-4o`
    * `gpt-4o-mini`
    * `gpt-4o-mini-2024-07-18`
    * `code-llama`
    * `codeqwen:v1.5-chat`

    If you wish to use a model not listed above, you can manually add its configuration (like the API endpoint URL) by modifying the `Model.java` file located at `src/main/java/zju/cst/aces/api/config/Model.java` in the `chatunitest-core` project. You would then need to rebuild the core library.

5.  **Q: I'm getting a "version not found" error for `chatunitest-core` or `chatunitest-maven-plugin`. What could be wrong?**

    **A:** This often happens if you are using an incorrect `groupId`. Please ensure you are using the correct and current `groupId`:

    * **Correct `groupId`:** `io.github.zju-aces-ise`
    * **Incorrect/Outdated `groupId`:** `io.github.ZJU-ACES-ISE` (note the capitalization)

    Using the outdated `groupId` will lead to "version not found" or "artifact not found" errors. Always double-check your `pom.xml` or dependency declarations.

6.  **Q: Where is the `tmpOutput` directory located? I can't find it in my project directory.**
    **A:** The `tmpOutput` directory, which contains information generated during the test construction process, defaults to being created in the root directory of the disk partition where your project is located, not directly inside your project's root folder. For example, if your project is at `/Users/mike/IdeaProjects/MyProject` (on macOS or Linux) or `D:\Projects\MyProject` (on Windows), the `tmpOutput` directory might be created at `/tmpOutput` or `D:\tmpOutput` respectively.

7.  **Q: I'm encountering an error related to [common issue, e.g., API authentication, test generation failure]. What are common troubleshooting steps?**
    **A:** If you encounter an error, try the following:

    * **Check API Key & LLM Configuration:** Ensure your LLM API key(s) are correctly set in the `<apiKeys>` tag, are valid, and have enough quota. Verify your LLM endpoint and model name configuration.
    * **Review Input Code:** Make sure the Java code for which you are generating tests is syntactically correct and accessible.
    * **Check Logs:** Look for detailed error messages in the console output. Running Maven with `-X` (debug) or `-e` (errors) can provide more details.
    * **Verify `tmpOutput` Location:** If the error relates to file operations, check the `tmpOutput` directory (see FAQ #6).
    * **Consult Documentation:** Review the relevant sections of our documentation for troubleshooting tips specific to the feature or error.
    * **Report an Issue:** If the problem persists, please raise an issue on our GitHub Issues page, providing as much detail as possible, including the error message, relevant parts of your configuration, and steps to reproduce the issue.