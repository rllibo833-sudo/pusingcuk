FROM debian:bookworm-slim AS build
ARG THRESHOLD_COMMIT=e367f45b0a35ccb8fdb91424099b8046b346d77d
ARG SUFFICIENCY_COMMIT=411c532454028d2d5e733373d085050eca1d402a
ARG THRESHOLD_SHA256=e79058b314d921a4b4353133b30a7a7b0da64d32785a39f66cb5ce356406067d
ARG SUFFICIENCY_SHA256=d6fcee54d17afbf0fc0a1aee115b2c0c9f57dcc172e56a6c6cf1d0dd9a789771
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates git gcc make libc6-dev && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /src/threshold /src/sufficiency /out /opt/rules \
 && git -C /src/threshold init \
 && git -C /src/threshold remote add origin https://github.com/rllibo833-sudo/pusingcuk.git \
 && git -C /src/threshold fetch --depth 1 origin "${THRESHOLD_COMMIT}" \
 && git -C /src/threshold checkout --detach FETCH_HEAD \
 && test "$(git -C /src/threshold rev-parse HEAD)" = "${THRESHOLD_COMMIT}" \
 && git -C /src/sufficiency init \
 && git -C /src/sufficiency remote add origin https://github.com/rllibo833-sudo/pusingcuk.git \
 && git -C /src/sufficiency fetch --depth 1 origin "${SUFFICIENCY_COMMIT}" \
 && git -C /src/sufficiency checkout --detach FETCH_HEAD \
 && test "$(git -C /src/sufficiency rev-parse HEAD)" = "${SUFFICIENCY_COMMIT}"
RUN test "$(sha256sum /src/threshold/examples/core/anggaran_threshold_service.cuk | cut -d' ' -f1)" = "${THRESHOLD_SHA256}" \
 && test "$(sha256sum /src/sufficiency/examples/core/anggaran_sufficiency_service.cuk | cut -d' ' -f1)" = "${SUFFICIENCY_SHA256}" \
 && make -C /src/threshold native CC=gcc NATIVE_BIN=/out/threshold-native \
 && make -C /src/sufficiency native CC=gcc NATIVE_BIN=/out/sufficiency-native \
 && test "$(/out/threshold-native --version)" = "Pusingcuk native 0.8.0.dev0" \
 && test "$(/out/sufficiency-native --version)" = "Pusingcuk native 0.8.0.dev0" \
 && cp /src/threshold/examples/core/anggaran_threshold_service.cuk /opt/rules/threshold.cuk \
 && cp /src/sufficiency/examples/core/anggaran_sufficiency_service.cuk /opt/rules/sufficiency.cuk

FROM debian:bookworm-slim
COPY --from=build /out/threshold-native /opt/threshold-native
COPY --from=build /out/sufficiency-native /opt/sufficiency-native
COPY --from=build /opt/rules/ /opt/rules/
COPY tools/sandbox/entrypoint.sh /opt/entrypoint.sh
RUN chmod 0555 /opt/threshold-native /opt/sufficiency-native /opt/entrypoint.sh \
 && chmod 0444 /opt/rules/threshold.cuk /opt/rules/sufficiency.cuk
USER 65534:65534
ENTRYPOINT ["/opt/entrypoint.sh"]
