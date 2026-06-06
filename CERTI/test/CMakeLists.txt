add_subdirectory(libgraphc)
add_subdirectory(Billard)
add_subdirectory(utility)
add_subdirectory(mom_explorer)
add_subdirectory(ModernBillard)
add_subdirectory(TimeMaster)
add_subdirectory(testFederate)

option(INSTALL_LEGACY_TEST_UTILITIES "Install legacy CERTI test utilities" OFF)

# Do not compile this on Win32 (not very useful)
if (NOT WIN32)
   if (CMAKE_SYSTEM_NAME MATCHES "Linux")
      set_source_files_properties(${CMAKE_CURRENT_SOURCE_DIR}/certiCheckHostAndIP.c PROPERTIES COMPILE_DEFINITIONS "LINUX")
   endif()
   add_executable(CertiCheckHostAndIP certiCheckHostAndIP.c)
   if (INSTALL_LEGACY_TEST_UTILITIES)
      install(TARGETS CertiCheckHostAndIP
              RUNTIME DESTINATION bin
              LIBRARY DESTINATION lib
              ARCHIVE DESTINATION lib)
   endif()
endif(NOT WIN32)
