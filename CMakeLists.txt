find_package(Python3 REQUIRED)

file(MAKE_DIRECTORY generate/devtools)

set(GENERATED_PROTOCOL_DIR ${CMAKE_CURRENT_SOURCE_DIR}/generate/devtools)

add_custom_target(generate_protocol
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND ${Python3_EXECUTABLE} generate_protocol.py --namespace devtools --output generate/devtools
                --templates templates --protocol protocol.json
        COMMENT "Generate protocol files"
        DEPENDS generate_protocol.py templates
)

set(DEVTOOLS_PROTOCOL_HEADER
         ${GENERATED_PROTOCOL_DIR}/Preload.h
         ${GENERATED_PROTOCOL_DIR}/Emulation.h
         ${GENERATED_PROTOCOL_DIR}/Values.h
         ${GENERATED_PROTOCOL_DIR}/Accessibility.h
         ${GENERATED_PROTOCOL_DIR}/Media.h
         ${GENERATED_PROTOCOL_DIR}/Overlay.h
         ${GENERATED_PROTOCOL_DIR}/Security.h
         ${GENERATED_PROTOCOL_DIR}/HeapProfiler.h
         ${GENERATED_PROTOCOL_DIR}/DOMSnapshot.h
         ${GENERATED_PROTOCOL_DIR}/Page.h
         ${GENERATED_PROTOCOL_DIR}/PerformanceTimeline.h
         ${GENERATED_PROTOCOL_DIR}/Performance.h
         ${GENERATED_PROTOCOL_DIR}/Database.h
         ${GENERATED_PROTOCOL_DIR}/Audits.h
         ${GENERATED_PROTOCOL_DIR}/DeviceOrientation.h
         ${GENERATED_PROTOCOL_DIR}/FedCm.h
         ${GENERATED_PROTOCOL_DIR}/LayerTree.h
         ${GENERATED_PROTOCOL_DIR}/ServiceWorker.h
         ${GENERATED_PROTOCOL_DIR}/Fetch.h
         ${GENERATED_PROTOCOL_DIR}/Console.h
         ${GENERATED_PROTOCOL_DIR}/Browser.h
         ${GENERATED_PROTOCOL_DIR}/Cast.h
         ${GENERATED_PROTOCOL_DIR}/HeadlessExperimental.h
         ${GENERATED_PROTOCOL_DIR}/Extensions.h
         ${GENERATED_PROTOCOL_DIR}/SystemInfo.h
         ${GENERATED_PROTOCOL_DIR}/WebAudio.h
         ${GENERATED_PROTOCOL_DIR}/Animation.h
         ${GENERATED_PROTOCOL_DIR}/Inspector.h
         ${GENERATED_PROTOCOL_DIR}/Storage.h
         ${GENERATED_PROTOCOL_DIR}/DOM.h
         ${GENERATED_PROTOCOL_DIR}/Memory.h
         ${GENERATED_PROTOCOL_DIR}/Tethering.h
         ${GENERATED_PROTOCOL_DIR}/Input.h
         ${GENERATED_PROTOCOL_DIR}/CacheStorage.h
         ${GENERATED_PROTOCOL_DIR}/Profiler.h
         ${GENERATED_PROTOCOL_DIR}/IndexedDB.h
         ${GENERATED_PROTOCOL_DIR}/IO.h
         ${GENERATED_PROTOCOL_DIR}/Network.h
         ${GENERATED_PROTOCOL_DIR}/DeviceAccess.h
         ${GENERATED_PROTOCOL_DIR}/CSS.h
         ${GENERATED_PROTOCOL_DIR}/DOMDebugger.h
         ${GENERATED_PROTOCOL_DIR}/Autofill.h
         ${GENERATED_PROTOCOL_DIR}/WebAuthn.h
         ${GENERATED_PROTOCOL_DIR}/Target.h
         ${GENERATED_PROTOCOL_DIR}/Debugger.h
         ${GENERATED_PROTOCOL_DIR}/PWA.h
         ${GENERATED_PROTOCOL_DIR}/Runtime.h
         ${GENERATED_PROTOCOL_DIR}/EventBreakpoints.h
         ${GENERATED_PROTOCOL_DIR}/Tracing.h
         ${GENERATED_PROTOCOL_DIR}/BackgroundService.h
         ${GENERATED_PROTOCOL_DIR}/Schema.h
         ${GENERATED_PROTOCOL_DIR}/Log.h
         ${GENERATED_PROTOCOL_DIR}/DOMStorage.h
)
set(DEVTOOLS_PROTOCOL_SOURCE
         ${GENERATED_PROTOCOL_DIR}/IndexedDB.cpp
         ${GENERATED_PROTOCOL_DIR}/ServiceWorker.cpp
         ${GENERATED_PROTOCOL_DIR}/DeviceAccess.cpp
         ${GENERATED_PROTOCOL_DIR}/IO.cpp
         ${GENERATED_PROTOCOL_DIR}/LayerTree.cpp
         ${GENERATED_PROTOCOL_DIR}/Extensions.cpp
         ${GENERATED_PROTOCOL_DIR}/Tracing.cpp
         ${GENERATED_PROTOCOL_DIR}/Database.cpp
         ${GENERATED_PROTOCOL_DIR}/Debugger.cpp
         ${GENERATED_PROTOCOL_DIR}/PWA.cpp
         ${GENERATED_PROTOCOL_DIR}/Animation.cpp
         ${GENERATED_PROTOCOL_DIR}/HeapProfiler.cpp
         ${GENERATED_PROTOCOL_DIR}/Schema.cpp
         ${GENERATED_PROTOCOL_DIR}/Overlay.cpp
         ${GENERATED_PROTOCOL_DIR}/Storage.cpp
         ${GENERATED_PROTOCOL_DIR}/WebAuthn.cpp
         ${GENERATED_PROTOCOL_DIR}/CacheStorage.cpp
         ${GENERATED_PROTOCOL_DIR}/Memory.cpp
         ${GENERATED_PROTOCOL_DIR}/Target.cpp
         ${GENERATED_PROTOCOL_DIR}/EventBreakpoints.cpp
         ${GENERATED_PROTOCOL_DIR}/SystemInfo.cpp
         ${GENERATED_PROTOCOL_DIR}/Autofill.cpp
         ${GENERATED_PROTOCOL_DIR}/Tethering.cpp
         ${GENERATED_PROTOCOL_DIR}/Emulation.cpp
         ${GENERATED_PROTOCOL_DIR}/Inspector.cpp
         ${GENERATED_PROTOCOL_DIR}/Media.cpp
         ${GENERATED_PROTOCOL_DIR}/Cast.cpp
         ${GENERATED_PROTOCOL_DIR}/DOMStorage.cpp
         ${GENERATED_PROTOCOL_DIR}/FedCm.cpp
         ${GENERATED_PROTOCOL_DIR}/DOMSnapshot.cpp
         ${GENERATED_PROTOCOL_DIR}/Runtime.cpp
         ${GENERATED_PROTOCOL_DIR}/DOM.cpp
         ${GENERATED_PROTOCOL_DIR}/WebAudio.cpp
         ${GENERATED_PROTOCOL_DIR}/Accessibility.cpp
         ${GENERATED_PROTOCOL_DIR}/Log.cpp
         ${GENERATED_PROTOCOL_DIR}/Security.cpp
         ${GENERATED_PROTOCOL_DIR}/Browser.cpp
         ${GENERATED_PROTOCOL_DIR}/Preload.cpp
         ${GENERATED_PROTOCOL_DIR}/DeviceOrientation.cpp
         ${GENERATED_PROTOCOL_DIR}/Console.cpp
         ${GENERATED_PROTOCOL_DIR}/CSS.cpp
         ${GENERATED_PROTOCOL_DIR}/Network.cpp
         ${GENERATED_PROTOCOL_DIR}/DOMDebugger.cpp
         ${GENERATED_PROTOCOL_DIR}/PerformanceTimeline.cpp
         ${GENERATED_PROTOCOL_DIR}/Performance.cpp
         ${GENERATED_PROTOCOL_DIR}/Fetch.cpp
         ${GENERATED_PROTOCOL_DIR}/Page.cpp
         ${GENERATED_PROTOCOL_DIR}/Audits.cpp
         ${GENERATED_PROTOCOL_DIR}/Profiler.cpp
         ${GENERATED_PROTOCOL_DIR}/BackgroundService.cpp
         ${GENERATED_PROTOCOL_DIR}/HeadlessExperimental.cpp
         ${GENERATED_PROTOCOL_DIR}/Input.cpp

         ${GENERATED_PROTOCOL_DIR}/Devtools.cpp
)

set_source_files_properties(${DEVTOOLS_PROTOCOL_HEADER} PROPERTIES GENERATED TRUE)
set_source_files_properties(${DEVTOOLS_PROTOCOL_SOURCE} PROPERTIES GENERATED TRUE)

add_library(devtools_protocol
        ${DEVTOOLS_PROTOCOL_HEADER}
        ${DEVTOOLS_PROTOCOL_SOURCE}
)
target_link_libraries(devtools_protocol
        tdutils)
target_include_directories(devtools_protocol
        PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/generate>
)
add_dependencies(devtools_protocol generate_protocol)