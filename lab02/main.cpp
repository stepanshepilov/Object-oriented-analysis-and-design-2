#define CPPHTTPLIB_OPENSSL_SUPPORT
#include "include/httplib.h"
#include <nlohmann/json.hpp>
#include <iostream>
#include <string>
#include <map>
#include <future>

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>

using json = nlohmann::json;

// Интерфейс для всех LLM сервисов
class ILLMService {
public:
    virtual ~ILLMService() {}
    virtual std::string ask(std::string prompt) = 0;
};

// LLM сервис без паттерна, умет прокидывать запрос на API Deepseek
class DeepSeekService : public ILLMService {
private:
    std::string apiKey;
public:
    DeepSeekService(std::string key) : apiKey(key) {}

    std::string ask(std::string prompt) override {
        httplib::Client cli("https://api.deepseek.com");
        cli.set_read_timeout(20, 0);

        json body = {
            {"model", "deepseek-chat"},
            {"messages", json::array({{{"role", "user"}, {"content", prompt}}})},
            {"stream", false}
        };

        httplib::Headers headers = {
            {"Authorization", "Bearer " + apiKey},
            {"Content-Type", "application/json"}
        };

        auto res = cli.Post("/chat/completions", headers, body.dump(), "application/json");
        if (res && res->status == 200) {
            try {
                auto jRes = json::parse(res->body);
                return jRes["choices"][0]["message"]["content"].get<std::string>();
            } catch (...) { return "Error parsing JSON response"; }
        }
        return "Error: " + (res ? std::to_string(res->status) : "Network connection failed");
    }
};

// GUI
void SetupModernStyle() {
    ImGuiStyle& style = ImGui::GetStyle();
    style.WindowRounding = 8.0f;
    style.FrameRounding = 6.0f;
    style.ChildRounding = 8.0f;
    
    ImVec4* colors = style.Colors;
    colors[ImGuiCol_WindowBg] = ImVec4(0.10f, 0.10f, 0.12f, 1.00f);
    colors[ImGuiCol_Button] = ImVec4(0.20f, 0.45f, 0.88f, 1.00f);
    colors[ImGuiCol_ButtonHovered] = ImVec4(0.26f, 0.59f, 0.98f, 1.00f);
    colors[ImGuiCol_FrameBg] = ImVec4(0.16f, 0.16f, 0.18f, 1.00f);
}

int main() {
    // Инициализация сервиса и прокси
    auto* real = new DeepSeekService("sk-83b8a79074014235a99ab723cb6e0103");

    if (!glfwInit()) return 1;
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);

    GLFWwindow* window = glfwCreateWindow(800, 600, "DeepSeek Proxy Lab", NULL, NULL);
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);

    // Инициализация ImGui
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    SetupModernStyle();
    ImGuiIO& io = ImGui::GetIO();

    const char* fontPaths[] = {
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Verdana.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf"
    };

    for (const char* path : fontPaths) {
        if (io.Fonts->AddFontFromFileTTF(path, 18.0f, NULL, io.Fonts->GetGlyphRangesCyrillic())) {
            std::cout << "Loaded: " << path << std::endl;
            break;
        }
    }

    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 150");

    char inputBuf[512] = "";
    std::string output = "Результат появится здесь...";
    bool isLoading = false;
    std::future<std::string> futureResult;

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        ImGui::SetNextWindowSize(io.DisplaySize);
        ImGui::SetNextWindowPos(ImVec2(0, 0));
        ImGui::Begin("Main", nullptr, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoResize);

        ImGui::TextColored(ImVec4(0.4f, 0.7f, 1.0f, 1.0f), "DeepSeek Proxy Interface (OOAP Lab)");
        ImGui::Separator();

        ImGui::Text("Введите ваш запрос:");
        ImGui::SetNextItemWidth(-1);
        ImGui::InputTextWithHint("##in", "Напишите что-нибудь...", inputBuf, IM_ARRAYSIZE(inputBuf));

        if (ImGui::Button("Отправить", ImVec2(120, 35)) && !isLoading) {
            std::string p(inputBuf);
            isLoading = true;
            futureResult = std::async(std::launch::async, [real, p]() { return real->ask(p); });
        }
        ImGui::SameLine();
        if (ImGui::Button("Тест RU", ImVec2(100, 35))) { output = "Проверка кириллицы: Привет!"; }

        ImGui::Separator();

        if (isLoading && futureResult.valid()) {
            if (futureResult.wait_for(std::chrono::milliseconds(0)) == std::future_status::ready) {
                output = futureResult.get();
                isLoading = false;
            }
            ImGui::TextColored(ImVec4(1, 1, 0, 1), "Нейросеть думает...");
        }

        ImGui::PushStyleColor(ImGuiCol_ChildBg, ImVec4(0.15f, 0.15f, 0.17f, 1.00f));
        ImGui::BeginChild("Out", ImVec2(0, 0), true);
        ImGui::TextWrapped("%s", output.c_str());
        ImGui::EndChild();
        ImGui::PopStyleColor();

        ImGui::End();

        ImGui::Render();
        int dw, dh;
        glfwGetFramebufferSize(window, &dw, &dh);
        glViewport(0, 0, dw, dh);
        glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
        glfwSwapBuffers(window);
    }

    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
