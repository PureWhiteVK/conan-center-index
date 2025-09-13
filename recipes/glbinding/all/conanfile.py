from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    copy,
    export_conandata_patches,
    get,
    rmdir,
    rm,
    replace_in_file,
)
import os

required_conan_version = ">=2.0.5"


class GlbindingConan(ConanFile):
    name = "glbinding"
    description = (
        "A C++ binding for the OpenGL API, generated using the gl.xml specification."
    )
    license = "MIT"
    topics = ("opengl", "binding")
    homepage = "https://glbinding.org/"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(
            self,
            file_path=os.path.join(self.source_folder, "CMakeLists.txt"),
            search='set(INSTALL_BIN       ".")',
            replace='set(INSTALL_BIN       "bin")',
        )
        replace_in_file(
            self,
            file_path=os.path.join(self.source_folder, "cmake", "CompileOptions.cmake"),
            search="/GL",
            replace="# /GL",
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["OPTION_SELF_CONTAINED"] = False
        tc.cache_variables["OPTION_BUILD_TESTS"] = False
        tc.cache_variables["OPTION_BUILD_DOCS"] = False
        tc.cache_variables["OPTION_BUILD_TOOLS"] = False
        tc.cache_variables["OPTION_BUILD_EXAMPLES"] = False
        tc.cache_variables["OPTION_BUILD_WITH_BOOST_THREAD"] = False
        tc.cache_variables["OPTION_BUILD_CHECK"] = False
        tc.cache_variables["OPTION_BUILD_OWN_KHR_HEADERS"] = True
        tc.cache_variables["OPTION_BUILD_WITH_LTO"] = False
        tc.cache_variables["OPTION_USE_GIT_INFORMATION"] = False
        tc.cache_variables["OPTION_ENABLE_COVERAGE"] = False
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, folder=self.package_folder, pattern="glbinding-config.cmake")
        rm(self, folder=self.package_folder, pattern="LICENSE")
        rm(self, folder=self.package_folder, pattern="README.md")
        rm(self, folder=self.package_folder, pattern="VERSION")
        rm(self, folder=self.package_folder, pattern="AUTHORS")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "glbinding")

        suffix = "d" if self.settings.build_type == "Debug" else ""
        # glbinding
        self.cpp_info.components["_glbinding"].set_property(
            "cmake_target_name", "glbinding::glbinding"
        )
        self.cpp_info.components["_glbinding"].libs = ["glbinding" + suffix]
        self.cpp_info.components["_glbinding"].requires = ["khrplatform"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_glbinding"].system_libs = ["dl", "pthread"]

        # glbinding-aux
        self.cpp_info.components["glbinding-aux"].set_property(
            "cmake_target_name", "glbinding::glbinding-aux"
        )
        self.cpp_info.components["glbinding-aux"].libs = ["glbinding-aux" + suffix]
        self.cpp_info.components["glbinding-aux"].requires = ["_glbinding"]

        # KHRplatform
        self.cpp_info.components["khrplatform"].set_property(
            "cmake_target_name", "glbinding::KHRplatform"
        )
        self.cpp_info.components["khrplatform"].libdirs = []
        self.cpp_info.components["khrplatform"].includedirs = [
            "include/glbinding/3rdparty"
        ]

        # workaround to propagate all components in CMakeDeps generator
        """
        since we have the dependency chain glbinding::glbinding-aux -> glbinding::glbinding -> glbinding::KHRplatform
        we can use glbinding::glbinding-aux to populate all targets here
        """
        self.cpp_info.set_property("cmake_target_name", "glbinding::glbinding-aux")
