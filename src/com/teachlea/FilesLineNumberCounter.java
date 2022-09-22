package com.teachlea;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class FilesLineNumberCounter {

    public static void main(String[] args) {
        String dirPath = "C:\\Users\\rajek\\Documents\\flexiWallet\\mobilePayment\\src\\main\\java\\com\\felxiwallet\\controller";
        String fileExtension = "java";
        try {
            List<String> files = findFiles(Paths.get(dirPath), fileExtension);
            files.forEach(x -> System.out.println("File " + fileName(x) + "  has  " + countLineBufferedReader(x) + " number of lines"));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static List<String> findFiles(Path path, String fileExtension)
            throws IOException {

        if (!Files.isDirectory(path)) {
            throw new IllegalArgumentException("Path must be a directory!");
        }

        List<String> result;

        try (Stream<Path> cakeWalk = Files.walk(path)) {
            result = cakeWalk
                    .filter(p -> !Files.isDirectory(p))
                    .map(p -> p.toString())
                    .filter(f -> f.endsWith(fileExtension))
                    .collect(Collectors.toList());
        }

        return result;
    }

    public static long countLineBufferedReader(String fileName) {

        long lines = 0;
        try (BufferedReader reader = new BufferedReader(new FileReader(fileName))) {
            while (reader.readLine() != null) lines++;
        } catch (IOException e) {
            e.printStackTrace();
        }
        return lines;

    }

    public static String fileName(String fname) {
        int pos = fname.lastIndexOf(File.separator);
        if (pos > -1)
            return fname.substring(pos + 1);
        else
            return fname;
    }
}
