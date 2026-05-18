#!/usr/bin/env swift
import Foundation
import Vision
import ImageIO

if CommandLine.arguments.count < 2 {
    fputs("usage: ocr_image.swift IMAGE_PATH\n", stderr)
    exit(2)
}

let imageURL = URL(fileURLWithPath: CommandLine.arguments[1])

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(url: imageURL, options: [:])
do {
    try handler.perform([request])
} catch {
    fputs("OCR failed: \(error)\n", stderr)
    exit(1)
}

let observations = request.results ?? []
let lines = observations.compactMap { observation in
    observation.topCandidates(1).first?.string
}
print(lines.joined(separator: "\n"))
