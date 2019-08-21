FROM python:3.7-alpine as builder

COPY requirements.txt /requirements.txt
RUN apk add --no-cache gcc musl-dev linux-headers && \
    pip3 install --install-option="--prefix=/install" -r requirements.txt
    
FROM python:3.7-alpine

COPY --from=builder /install /usr/local

WORKDIR /onkyo_exporter
COPY onkyo_exporter.py .

ENTRYPOINT ["./onkyo_exporter.py"]